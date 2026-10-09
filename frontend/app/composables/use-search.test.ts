import { ref } from "vue";
import { describe, expect, test } from "vitest";
import type { ISearchableItem } from "./use-search";
import { useSearch } from "./use-search";

function item(name: string, extra: Partial<ISearchableItem> = {}): ISearchableItem {
  return { id: name, name, ...extra };
}

/**
 * `filtered` reads `debouncedSearch`, which is normally populated by a debounced
 * watcher. Setting it directly keeps these tests synchronous.
 */
function searchFor(items: ISearchableItem[], query: string) {
  const { debouncedSearch, filtered } = useSearch(ref(items));
  debouncedSearch.value = query;
  return filtered.value.map(i => i.name);
}

describe("useSearch ranking tiers", () => {
  test("exact match outranks prefix, word-prefix, and substring", () => {
    const names = searchFor([
      item("flatbread"),
      item("banana bread"),
      item("breadsticks"),
      item("bread"),
    ], "bread");

    expect(names).toEqual(["bread", "breadsticks", "banana bread", "flatbread"]);
  });

  test("word-prefix match outranks a mid-word substring match", () => {
    const names = searchFor([
      item("shortbread"),
      item("corn bread"),
    ], "bread");

    expect(names).toEqual(["corn bread", "shortbread"]);
  });

  test("substring matches are still returned when nothing stronger matches", () => {
    const names = searchFor([
      item("unsweetened cocoa"),
      item("flour"),
    ], "cocoa");

    expect(names).toEqual(["unsweetened cocoa"]);
  });

  test("fuzzy tier tolerates typos and ranks below deterministic matches", () => {
    const names = searchFor([
      item("bannana"),
      item("banana pepper"),
    ], "banana");

    expect(names[0]).toBe("banana pepper");
    expect(names).toContain("bannana");
  });

  test("fuzzy tier matches a typo'd query", () => {
    const names = searchFor([item("banana"), item("cinnamon")], "bannana");
    expect(names).toContain("banana");
  });

  test("items matching no tier are dropped", () => {
    const names = searchFor([item("bread"), item("olive oil")], "bread");
    expect(names).toEqual(["bread"]);
  });

  test("ties within a tier break on shortest match, then alphabetically", () => {
    const names = searchFor([
      item("sugar snap peas"),
      item("snap peas"),
      item("snap beans"),
      item("snap corn"),
      item("peas snap"),
    ], "snap");

    expect(names).toEqual([
      "snap corn",
      "snap peas",
      "snap beans",
      "peas snap",
      "sugar snap peas",
    ]);
  });

  test("aliases, plurals, and abbreviations participate in ranking", () => {
    const names = searchFor([
      item("granulated sugar", { abbreviation: "sug" }),
      item("tablespoon", { pluralName: "tablespoons", abbreviation: "tbsp", aliases: [{ name: "big spoon" }] }),
    ], "tbsp");

    expect(names).toEqual(["tablespoon"]);
  });

  test("matching is diacritic- and case-insensitive", () => {
    const names = searchFor([item("Jalapeño"), item("onion")], "JALAPENO");
    expect(names).toEqual(["Jalapeño"]);
  });

  test("empty or too-short queries return every item unchanged", () => {
    const items = [item("bread"), item("olive oil")];
    const { debouncedSearch, filtered } = useSearch(ref(items));

    expect(filtered.value).toEqual(items);
    debouncedSearch.value = "   ";
    expect(filtered.value).toEqual(items);
  });

  test("regex metacharacters in the query are treated literally", () => {
    const names = searchFor([item("half & half"), item("a.b"), item("axb")], "a.b");
    expect(names).toEqual(["a.b"]);
  });
});
