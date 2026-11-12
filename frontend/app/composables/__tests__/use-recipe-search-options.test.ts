import { describe, expect, test } from "vitest";
import { recipeSortOptions } from "../use-recipe-search-options";

describe("recipe search options", () => {
  test("offers both directions for each field and one random choice", () => {
    for (const field of ["name", "rating", "created_at", "updated_at", "last_made", "total_time_seconds"]) {
      expect(recipeSortOptions.filter(([name]) => name === field).map(([, direction]) => direction).sort()).toEqual(["asc", "desc"]);
    }
    expect(recipeSortOptions.filter(([name]) => name === "random")).toHaveLength(1);
  });
});
