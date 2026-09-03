import { ref } from "vue";
import { describe, expect, test } from "vitest";
import { useShoppingListSearch } from "./use-shopping-list-search";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

function listItem(id: string, overrides: Partial<ShoppingListItemOut> = {}): ShoppingListItemOut {
  return {
    id,
    shoppingListId: "list",
    groupId: "group",
    householdId: "household",
    ...overrides,
  } as ShoppingListItemOut;
}

/**
 * `matchesSearch` reads `debouncedSearch`, which is normally populated by a
 * debounced watcher. Setting it directly keeps these tests synchronous, as in
 * use-search.test.ts.
 */
function searchFor(items: ShoppingListItemOut[], query: string) {
  const composable = useShoppingListSearch(ref(items));
  composable.debouncedSearch.value = query;
  return composable;
}

describe("useShoppingListSearch matching", () => {
  test("an empty query matches every item and is not 'searching'", () => {
    const items = [listItem("a", { note: "Kitchen roll" }), listItem("b", { note: "Bread" })];
    const { isSearching, matchesSearch, countMatches, hasMatches } = searchFor(items, "");

    expect(isSearching.value).toBe(false);
    expect(items.every(matchesSearch)).toBe(true);
    expect(countMatches(items)).toBe(2);
    expect(hasMatches(items)).toBe(true);
  });

  test("matches a note-only item by its note text", () => {
    const items = [listItem("a", { note: "Kitchen roll" }), listItem("b", { note: "Bread" })];
    const { matchesSearch } = searchFor(items, "kitchen");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["a"]);
  });

  test("matches a food-backed item by food name", () => {
    const items = [
      listItem("a", { food: { id: "f1", name: "Avocado" } }),
      listItem("b", { food: { id: "f2", name: "Bread" } }),
    ];
    const { matchesSearch } = searchFor(items, "avocado");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["a"]);
  });

  test("matches a food-backed item by its note as well as its food", () => {
    const items = [
      listItem("a", { food: { id: "f1", name: "Avocado" }, note: "ripe ones" }),
      listItem("b", { food: { id: "f2", name: "Bread" } }),
    ];
    const { matchesSearch } = searchFor(items, "ripe");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["a"]);
  });

  test("matches a food alias", () => {
    const items = [
      listItem("a", { food: { id: "f1", name: "Aubergine", aliases: [{ name: "Eggplant" }] } }),
      listItem("b", { food: { id: "f2", name: "Bread" } }),
    ];
    const { matchesSearch } = searchFor(items, "eggplant");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["a"]);
  });

  test("matches on label name, so searching an aisle narrows the list to it", () => {
    const items = [
      listItem("a", { note: "Persil Non Bio", label: { name: "Laundry" } }),
      listItem("b", { note: "Comfort Fresh", label: { name: "Laundry" } }),
      listItem("c", { note: "Bread", label: { name: "Bakery" } }),
    ];
    const { matchesSearch, countMatches } = searchFor(items, "laundry");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["a", "b"]);
    expect(countMatches(items)).toBe(2);
  });

  test("a query that matches nothing yields no matches", () => {
    const items = [listItem("a", { note: "Kitchen roll" }), listItem("b", { note: "Bread" })];
    const { matchesSearch, countMatches, hasMatches } = searchFor(items, "zzzznope");

    expect(items.some(matchesSearch)).toBe(false);
    expect(countMatches(items)).toBe(0);
    expect(hasMatches(items)).toBe(false);
  });

  test("clearSearch restores every item", () => {
    const items = [listItem("a", { note: "Kitchen roll" }), listItem("b", { note: "Bread" })];
    const composable = searchFor(items, "bread");
    expect(composable.countMatches(items)).toBe(1);

    composable.clearSearch();
    expect(composable.isSearching.value).toBe(false);
    expect(composable.countMatches(items)).toBe(2);
  });
});
