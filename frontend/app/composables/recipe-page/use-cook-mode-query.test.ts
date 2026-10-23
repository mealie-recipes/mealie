import { computed, nextTick, ref } from "vue";
import { describe, expect, test } from "vitest";
import { PageMode } from "./shared-state";
import { useCookModeQuery, type BooleanString } from "./use-cook-mode-query";

function buildHarness(initialCookQuery: BooleanString | undefined = undefined, initialMode = PageMode.VIEW) {
  const cookQuery = ref<BooleanString | undefined>(initialCookQuery);
  const queryWrites: (BooleanString | undefined)[] = [];
  const pageMode = ref(initialMode);

  const setMode = (mode: PageMode) => {
    pageMode.value = mode;
  };

  const sync = useCookModeQuery({
    cookQuery: computed({
      get: () => cookQuery.value,
      set: (value) => {
        queryWrites.push(value);
        cookQuery.value = value;
      },
    }),
    isEditMode: computed(() => pageMode.value === PageMode.EDIT),
    pageMode: computed(() => pageMode.value),
    setMode,
  });

  return {
    cookQuery,
    queryWrites,
    pageMode,
    setMode,
    ...sync,
  };
}

function buildAsyncHarness(initialCookQuery: BooleanString | undefined = undefined, initialMode = PageMode.VIEW) {
  const routeCookQuery = ref<BooleanString | undefined>(initialCookQuery);
  const pageMode = ref(initialMode);

  const setMode = (mode: PageMode) => {
    pageMode.value = mode;
  };

  const sync = useCookModeQuery({
    cookQuery: computed({
      get: () => routeCookQuery.value,
      set: (value) => {
        nextTick(() => {
          routeCookQuery.value = value;
        });
      },
    }),
    isEditMode: computed(() => pageMode.value === PageMode.EDIT),
    pageMode: computed(() => pageMode.value),
    setMode,
  });

  return {
    cookQuery: routeCookQuery,
    pageMode,
    setMode,
    ...sync,
  };
}

describe("useCookModeQuery", () => {
  test.each([undefined, ""] as const)("does not write an absent cook query (%s) when saving edits", async (initialCookQuery) => {
    const harness = buildHarness(initialCookQuery, PageMode.EDIT);

    harness.hydrateCookMode();
    harness.setMode(PageMode.VIEW);
    await nextTick();

    // A query write schedules navigation and can cancel the recipe rename redirect.
    expect(harness.queryWrites).toEqual([]);
    expect(harness.pageMode.value).toBe(PageMode.VIEW);
  });

  test("hydrates cook mode from the query", async () => {
    const harness = buildHarness("true");

    harness.hydrateCookMode();
    await nextTick();

    expect(harness.pageMode.value).toBe(PageMode.COOK);
  });

  test("does not enter cook mode while edit mode is active", async () => {
    const harness = buildHarness("true", PageMode.EDIT);

    harness.hydrateCookMode();
    await nextTick();

    expect(harness.pageMode.value).toBe(PageMode.EDIT);
    expect(harness.cookQuery.value).toBe("true");
  });

  test("enters cook mode after leaving edit mode if the query is still set", async () => {
    const harness = buildHarness("true", PageMode.EDIT);

    harness.hydrateCookMode();
    harness.setMode(PageMode.VIEW);
    await nextTick();

    expect(harness.pageMode.value).toBe(PageMode.COOK);
  });

  test("writes cook=true when cook mode is entered from the UI", async () => {
    const harness = buildHarness();

    harness.hydrateCookMode();
    harness.setMode(PageMode.COOK);
    await nextTick();

    expect(harness.cookQuery.value).toBe("true");
  });

  test("removes the query when cook mode is exited to view mode", async () => {
    const harness = buildHarness("true", PageMode.COOK);

    harness.hydrateCookMode();
    harness.setMode(PageMode.VIEW);
    await nextTick();

    expect(harness.cookQuery.value).toBeUndefined();
  });

  test("reacts to route query changes after hydration", async () => {
    const harness = buildHarness();

    harness.hydrateCookMode();
    harness.cookQuery.value = "true";
    await nextTick();

    expect(harness.pageMode.value).toBe(PageMode.COOK);

    harness.cookQuery.value = undefined;
    await nextTick();

    expect(harness.pageMode.value).toBe(PageMode.VIEW);
  });

  test("clears a pending cook query when cook mode is entered and exited in the same tick", async () => {
    const harness = buildAsyncHarness();

    harness.hydrateCookMode();
    harness.setMode(PageMode.COOK);
    harness.setMode(PageMode.VIEW);
    await nextTick();
    await nextTick();

    expect(harness.cookQuery.value).toBeUndefined();
    expect(harness.pageMode.value).toBe(PageMode.VIEW);
  });

  test("clears cook mode while its query navigation is still pending", async () => {
    const queryWrites: (BooleanString | undefined)[] = [];
    const pageMode = ref(PageMode.VIEW);
    const setMode = (mode: PageMode) => {
      pageMode.value = mode;
    };
    const sync = useCookModeQuery({
      cookQuery: computed<BooleanString | undefined>({
        get: () => undefined,
        // The router has not applied these writes to the current route yet.
        set: value => queryWrites.push(value),
      }),
      isEditMode: computed(() => pageMode.value === PageMode.EDIT),
      pageMode: computed(() => pageMode.value),
      setMode,
    });

    sync.hydrateCookMode();
    setMode(PageMode.COOK);
    await nextTick();
    setMode(PageMode.VIEW);
    await nextTick();

    expect(queryWrites).toEqual(["true", undefined]);
    expect(pageMode.value).toBe(PageMode.VIEW);
  });
});
