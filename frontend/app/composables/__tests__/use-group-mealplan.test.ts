import { describe, expect, test, vi } from "vitest";
import { getScaledRecipes, getWeekRange } from "../use-group-mealplan";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({}),
}));

function createMeal(id: number, overrides: Partial<ReadPlanEntry> = {}): ReadPlanEntry {
  return {
    id,
    date: "2026-08-19",
    entryType: "dinner",
    groupId: "my-group-id",
    userId: "my-user-id",
    householdId: "my-household-id",
    ...overrides,
  };
}

describe("getScaledRecipes", () => {
  test("gives each recipe the scale of its entry", () => {
    const pancakes = { id: "pancakes", name: "Pancakes" };
    const waffles = { id: "waffles", name: "Waffles" };

    expect(getScaledRecipes([
      createMeal(1, { recipe: pancakes, recipeScale: 2 }),
      createMeal(2, { recipe: waffles, recipeScale: 0.5 }),
    ])).toEqual([
      { ...pancakes, scale: 2 },
      { ...waffles, scale: 0.5 },
    ]);
  });

  test("keeps a recipe that's planned twice as two entries with their own scales", () => {
    const pancakes = { id: "pancakes", name: "Pancakes" };

    const recipes = getScaledRecipes([
      createMeal(1, { recipe: pancakes, recipeScale: 2 }),
      createMeal(2, { recipe: pancakes, recipeScale: 3 }),
    ]);

    expect(recipes.map(({ scale }) => scale)).toEqual([2, 3]);
  });

  test("treats an entry without a scale as unscaled", () => {
    const recipes = getScaledRecipes([createMeal(1, { recipe: { id: "pancakes" } })]);
    expect(recipes.map(({ scale }) => scale)).toEqual([1]);
  });

  test("skips notes", () => {
    expect(getScaledRecipes([
      createMeal(1, { title: "Leftovers" }),
      createMeal(2, { title: "Eat out", recipe: null }),
    ])).toEqual([]);
  });
});

describe("getWeekRange", () => {
  // 2026-08-19 is a Wednesday
  const wednesday = new Date(2026, 7, 19);

  test.each([
    [0, new Date(2026, 7, 16), new Date(2026, 7, 22)],
    [1, new Date(2026, 7, 17), new Date(2026, 7, 23)],
    [4, new Date(2026, 7, 13), new Date(2026, 7, 19)],
  ])("starts the week on day %i", (firstDayOfWeek, start, end) => {
    expect(getWeekRange(wednesday, firstDayOfWeek)).toEqual({ start, end });
  });
});
