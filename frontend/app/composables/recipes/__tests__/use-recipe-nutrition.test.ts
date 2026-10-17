import { describe, expect, test } from "vitest";
import { estimateNutritionPer100g, estimateRecipeWeightGrams, parseNutritionValue } from "../use-recipe-nutrition";
import type { Nutrition, RecipeIngredient } from "~/lib/api/types/recipe";

function ingredient(quantity: number | null, standardUnit: string | null, standardQuantity = 1): RecipeIngredient {
  return {
    quantity: quantity ?? undefined,
    unit: standardUnit ? { id: "u", name: standardUnit, standardUnit, standardQuantity } : undefined,
  };
}

describe("parseNutritionValue", () => {
  test.each([
    ["18g", 18],
    ["450 mg", 450],
    ["320 calories", 320],
    ["4.5 g", 4.5],
    ["0", 0],
    ["", null],
    [null, null],
    [undefined, null],
    ["unknown", null],
    ["Infinity", null],
  ])("parses %j as %j", (value, expected) => {
    expect(parseNutritionValue(value)).toBe(expected);
  });
});

describe("estimateRecipeWeightGrams", () => {
  test("sums mass units directly and ignores unconvertible ingredients", () => {
    const ingredients = [
      ingredient(500, "gram"),
      ingredient(2, "kilogram"),
      ingredient(2, null), // e.g. "2 eggs" - no weighable unit
      ingredient(null, "gram"), // no quantity at all
    ];

    const result = estimateRecipeWeightGrams(ingredients);
    expect(result.grams).toBe(2500);
    expect(result.matched).toBe(2);
    expect(result.total).toBe(3);
  });

  test("approximates volume as water density", () => {
    const result = estimateRecipeWeightGrams([ingredient(250, "milliliter")]);
    expect(result.grams).toBe(250);
    expect(result.matched).toBe(1);
  });

  test("returns zero weight and counts when nothing is convertible", () => {
    const result = estimateRecipeWeightGrams([ingredient(1, null)]);
    expect(result).toEqual({ grams: 0, matched: 0, total: 1 });
  });
});

describe("estimateNutritionPer100g", () => {
  const nutrition: Nutrition = { calories: "100", proteinContent: "10", fatContent: null };

  test("scales per-serving values to per-100g using the given weight", () => {
    const result = estimateNutritionPer100g(nutrition, 50);
    expect(result.calories).toBe("200.00");
    expect(result.proteinContent).toBe("20.00");
    expect(result.fatContent).toBeNull();
  });

  test("leaves values untouched when the weight is not usable", () => {
    expect(estimateNutritionPer100g(nutrition, 0)).toEqual(nutrition);
    expect(estimateNutritionPer100g(nutrition, -5)).toEqual(nutrition);
  });
});
