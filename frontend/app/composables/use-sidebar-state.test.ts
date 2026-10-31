import { nextTick, ref } from "vue";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { useSidebarState } from "./use-sidebar-state";

const mocks = vi.hoisted(() => ({
  sidebarQuery: { value: "" },
  largeScreen: true,
}));

vi.mock("~/composables/use-router", () => ({
  useRouteQuery: () => mocks.sidebarQuery,
}));

describe("useSidebarState", () => {
  beforeEach(() => {
    localStorage.clear();
    mocks.sidebarQuery.value = "";
    mocks.largeScreen = true;
    vi.stubGlobal("useDisplay", () => ({ lgAndUp: ref(mocks.largeScreen) }));
  });

  afterEach(() => vi.unstubAllGlobals());

  test("uses screen size when there is no saved preference", () => {
    expect(useSidebarState().value).toBe(true);

    mocks.largeScreen = false;
    expect(useSidebarState().value).toBe(false);
  });

  test.each([true, false])("restores saved preference %s as a boolean without a URL override", async (saved) => {
    const sidebar = useSidebarState();
    sidebar.value = saved;
    await nextTick();

    expect(localStorage.getItem("sidebar-open")).toBe(String(saved));
    expect(useSidebarState().value).toBe(saved);
  });

  test.each([
    ["true", false, true],
    ["false", true, false],
  ] as const)("lets sidebar=%s in the URL override saved state", (query, saved, expected) => {
    localStorage.setItem("sidebar-open", JSON.stringify(saved));
    mocks.sidebarQuery.value = query;

    expect(useSidebarState().value).toBe(expected);
  });

  test("updates the URL and storage when toggled with an explicit URL parameter", async () => {
    mocks.sidebarQuery.value = "false";
    const sidebar = useSidebarState();
    sidebar.value = true;
    await nextTick();

    expect(mocks.sidebarQuery.value).toBe("true");
    expect(localStorage.getItem("sidebar-open")).toBe("true");
  });
});
