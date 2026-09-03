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

describe("useShoppingListSearch fuzzy noise", () => {
  test("does not match items that merely look similar to the query", () => {
    // Grouping the list by label removes any notion of a weaker match sorting
    // lower, so a fuzzy hit would read as a real one. These are the cases a
    // fuzzy tier actually produced against a real list.
    const items = [
      listItem("wash-liquid", { note: "Washing up liquid" }),
      listItem("wash-gloves", { note: "Washing up gloves" }),
      listItem("stash", { note: "Extra chocolate treat - secret surprise stash" }),
      listItem("cash", { note: "Get cash out" }),
    ];
    const { matchesSearch } = searchFor(items, "cash");

    expect(items.filter(matchesSearch).map(i => i.id)).toEqual(["cash"]);
  });

  test("a query with no real match returns nothing rather than a near-miss", () => {
    const items = [
      listItem("a", { note: "Twinings honey & camomile tea" }),
      listItem("b", { note: "Toilet paper, family pack of 16" }),
    ];
    const { matchesSearch, hasMatches } = searchFor(items, "milk");

    expect(items.some(matchesSearch)).toBe(false);
    expect(hasMatches(items)).toBe(false);
  });

  test("a multi-word query matches as a phrase, like every other search in the app", () => {
    // useSearch matches the query as a single string rather than as independent
    // terms, so word order matters. Kept as a test because it is the one
    // behaviour that differs from a naive per-term matcher.
    const items = [
      listItem("beans", { note: "Green beans, bags" }),
      listItem("peppers", { note: "Green peppers" }),
    ];

    expect(items.filter(searchFor(items, "green bean").matchesSearch).map(i => i.id))
      .toEqual(["beans"]);
    expect(items.filter(searchFor(items, "bean green").matchesSearch))
      .toEqual([]);
  });
});
