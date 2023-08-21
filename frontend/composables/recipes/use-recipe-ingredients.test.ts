import { describe, test, expect } from "vitest";
import { parseIngredientText } from "./use-recipe-ingredients";
import { RecipeIngredient } from "~/lib/api/types/recipe";

describe(parseIngredientText.name, () => {
  const createRecipeIngredient = (overrides: Partial<RecipeIngredient>): RecipeIngredient => ({
    quantity: 1,
    food: {
      id: "1",
      name: "Item 1",
    },
    unit: {
      id: "1",
      name: "cup",
    },
    ...overrides,
  });

  test("uses ingredient note if disableAmount: true", () => {
    const ingredient = createRecipeIngredient({ note: "foo" });

    expect(parseIngredientText(ingredient, true)).toEqual("foo");
  });

  test("adds note section if note present", () => {
    const ingredient = createRecipeIngredient({ note: "custom note" });

    expect(parseIngredientText(ingredient, false)).toContain("custom note");
  });

  test("ingredient text with fraction", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: { fraction: true, id: "1", name: "cup" } });

    expect(parseIngredientText(ingredient, false)).contain("1 <sup>1</sup>").and.to.contain("<sub>2</sub>");
  });

  test("sanitizes html", () => {
    const ingredient = createRecipeIngredient({ note: "<script>alert('foo')</script>" });

    expect(parseIngredientText(ingredient, false)).not.toContain("<script>");
  });
});
