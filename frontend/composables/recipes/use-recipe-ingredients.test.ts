import { describe, test, expect } from "vitest";
import { parseIngredientText } from "./use-recipe-ingredients";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

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

  test("adds note section if note present", () => {
    const ingredient = createRecipeIngredient({ note: "custom note" });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toContain("custom note");
  });

  test("ingredient text with fraction", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: { fraction: true, id: "1", name: "cup" } });

    expect(parseIngredientText(ingredient, 1, true, "always_pluralize")).contain("1<sup>1</sup>").and.to.contain("<sub>2</sub>");
  });

  test("ingredient text with fraction when unit is null", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: undefined });

    expect(parseIngredientText(ingredient, 1, true, "always_pluralize")).contain("1<sup>1</sup>").and.to.contain("<sub>2</sub>");
  });

  test("ingredient text with fraction no formatting", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: { fraction: true, id: "1", name: "cup" } });
    const result = parseIngredientText(ingredient, 1, false, "always_pluralize");

    expect(result).not.contain("<");
    expect(result).not.contain(">");
    expect(result).contain("1 1/2");
  });

  test("sanitizes html", () => {
    const ingredient = createRecipeIngredient({ note: "<script>alert('foo')</script>" });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).not.toContain("<script>");
  });

  test("plural test : plural qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("2 tbsps diced onions");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("2 tbsps diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("2 tbsps diced onion");
  });

  test("plural test : plural qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("2 tablespoons diced onions");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("2 tablespoons diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("2 tablespoons diced onion");
  });

  test("plural test : single qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("1 tbsp diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("1 tbsp diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("1 tbsp diced onion");
  });

  test("plural test : single qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("1 tablespoon diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("1 tablespoon diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("1 tablespoon diced onion");
  });

  test("plural test : small qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.5,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("0.5 tbsp diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("0.5 tbsp diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("0.5 tbsp diced onion");
  });

  test("plural test : small qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.5,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("0.5 tablespoon diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("0.5 tablespoon diced onion");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("0.5 tablespoon diced onion");
  });

  test("plural test : zero qty", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("diced onions");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("diced onions");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("diced onion");
  });

  test("plural test : single qty, scaled", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, 2, undefined, "always_pluralize")).toEqual("2 tablespoons diced onions");
    expect(parseIngredientText(ingredient, 2, undefined, "pluralize_food_without_unit")).toEqual("2 tablespoons diced onion");
    expect(parseIngredientText(ingredient, 2, undefined, "disable")).toEqual("2 tablespoons diced onion");
  });

  test("plural test : no unit", () => {
    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: undefined,
      food: { id: "1", name: "apple", pluralName: "apples" },
    });

    expect(parseIngredientText(ingredient, undefined, undefined, "always_pluralize")).toEqual("2 apples");
    expect(parseIngredientText(ingredient, undefined, undefined, "pluralize_food_without_unit")).toEqual("2 apples");
    expect(parseIngredientText(ingredient, undefined, undefined, "disable")).toEqual("2 apple");
  });
});
