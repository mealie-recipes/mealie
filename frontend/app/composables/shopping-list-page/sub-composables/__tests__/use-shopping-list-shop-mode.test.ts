import { computed, nextTick, ref } from "vue";
import { describe, expect, test } from "vitest";
import { useShoppingListShopMode } from "../use-shopping-list-shop-mode";
import { MOCK_ITEM } from "./mocks";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

function buildHarness(initialQuery: string | undefined = undefined) {
  const routeQuery = ref<string | undefined>(initialQuery);
  const itemsByLabel = ref<{ [key: string]: ShoppingListItemOut[] }>({});
  const mode = useShoppingListShopMode({
    // like useRouteQuery, the write only lands on the next tick
    shopQuery: computed({
      get: () => routeQuery.value,
      set: (value) => {
        nextTick(() => {
          routeQuery.value = value ?? undefined;
        });
      },
    }),
    itemsByLabel,
  });
  return { routeQuery, itemsByLabel, ...mode };
}

describe("useShoppingListShopMode", () => {
  describe("query", () => {
    test("is off without the query", () => {
      expect(buildHarness().isShopMode.value).toBe(false);
    });

    test("starts on from the query, so a reload keeps the mode", () => {
      expect(buildHarness("true").isShopMode.value).toBe(true);
    });

    test.each(["false", ""])("ignores the query value '%s'", (value) => {
      expect(buildHarness(value).isShopMode.value).toBe(false);
    });

    test("entering writes the query", async () => {
      const { routeQuery, isShopMode, enterShopMode } = buildHarness();
      enterShopMode();
      await nextTick();
      expect(routeQuery.value).toBe("true");
      expect(isShopMode.value).toBe(true);
    });

    test("leaving removes the query", async () => {
      const { routeQuery, isShopMode, exitShopMode } = buildHarness("true");
      exitShopMode();
      await nextTick();
      expect(routeQuery.value).toBeUndefined();
      expect(isShopMode.value).toBe(false);
    });

    test("follows outside changes of the query", async () => {
      const { routeQuery, isShopMode } = buildHarness();
      routeQuery.value = "true";
      await nextTick();
      expect(isShopMode.value).toBe(true);
    });
  });

  describe("completed switch", () => {
    test("is off by default", () => {
      expect(buildHarness("true").showChecked.value).toBe(false);
    });

    test("is off again after leaving and entering", async () => {
      const { showChecked, enterShopMode, exitShopMode } = buildHarness("true");
      showChecked.value = true;

      exitShopMode();
      await nextTick();
      await nextTick();
      expect(showChecked.value).toBe(false);

      enterShopMode();
      await nextTick();
      await nextTick();
      expect(showChecked.value).toBe(false);
    });

    test("is not written to local storage", () => {
      const { showChecked } = buildHarness("true");
      const keysBefore = Object.keys(window.localStorage ?? {});
      showChecked.value = true;
      expect(Object.keys(window.localStorage ?? {})).toEqual(keysBefore);
    });
  });

  describe("sections", () => {
    test("keep the label order and drop empty labels", () => {
      const { itemsByLabel, sections } = buildHarness("true");
      const a = { ...MOCK_ITEM, id: "a" };
      const b = { ...MOCK_ITEM, id: "b" };
      itemsByLabel.value = { Produce: [a], Empty: [], Dairy: [b] };
      expect(sections.value.map(section => section.label)).toEqual(["Produce", "Dairy"]);
    });

    test("count what is left", () => {
      const { itemsByLabel, remainingCount } = buildHarness("true");
      expect(remainingCount.value).toBe(0);
      itemsByLabel.value = {
        Produce: [{ ...MOCK_ITEM, id: "a" }, { ...MOCK_ITEM, id: "b" }],
        Dairy: [{ ...MOCK_ITEM, id: "c" }],
      };
      expect(remainingCount.value).toBe(3);
    });
  });
});
