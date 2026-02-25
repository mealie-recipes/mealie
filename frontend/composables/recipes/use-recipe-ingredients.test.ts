import { describe, test, expect, vi, beforeEach } from "vitest";
import { useIngredientTextParser } from "./use-recipe-ingredients";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import { useLocales } from "../use-locales";

vi.mock("../use-locales");

let parseIngredientText: (ingredient: RecipeIngredient, scale?: number, includeFormating?: boolean) => string;

describe("parseIngredientText", () => {
  beforeEach(() => {
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "always" }],
      locale: { value: "en-US", pluralFoodHandling: "always" },
    } as any);
    ({ parseIngredientText } = useIngredientTextParser());
  });

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

    expect(parseIngredientText(ingredient)).toContain("custom note");
  });

  test("ingredient text with fraction", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: { fraction: true, id: "1", name: "cup" } });

    expect(parseIngredientText(ingredient, 1, true)).contain("1<sup>1</sup>").and.to.contain("<sub>2</sub>");
  });

  test("ingredient text with fraction when unit is null", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: undefined });

    expect(parseIngredientText(ingredient, 1, true)).contain("1<sup>1</sup>").and.to.contain("<sub>2</sub>");
  });

  test("ingredient text with fraction no formatting", () => {
    const ingredient = createRecipeIngredient({ quantity: 1.5, unit: { fraction: true, id: "1", name: "cup" } });
    const result = parseIngredientText(ingredient, 1, false);

    expect(result).not.contain("<");
    expect(result).not.contain(">");
    expect(result).contain("1 1/2");
  });

  test("sanitizes html", () => {
    const ingredient = createRecipeIngredient({ note: "<script>alert('foo')</script>" });

    expect(parseIngredientText(ingredient)).not.toContain("<script>");
  });

  test("plural test : plural qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tbsps diced onions");
  });

  test("plural test : plural qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tablespoons diced onions");
  });

  test("plural test : single qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("1 tbsp diced onion");
  });

  test("plural test : single qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("1 tablespoon diced onion");
  });

  test("plural test : small qty : use abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.5,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: true },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("0.5 tbsp diced onion");
  });

  test("plural test : small qty : not abbreviation", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.5,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("0.5 tablespoon diced onion");
  });

  test("plural test : zero qty", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("diced onions");
  });

  test("plural test : single qty, scaled", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", abbreviation: "tbsp", pluralAbbreviation: "tbsps", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient, 2)).toEqual("2 tablespoons diced onions");
  });

  test("plural handling: 'always' strategy uses plural food with unit", () => {
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "always" }],
      locale: { value: "en-US", pluralFoodHandling: "always" },
    } as any);
    const { parseIngredientText } = useIngredientTextParser();

    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tablespoons diced onions");
  });

  test("plural handling: 'never' strategy never uses plural food", () => {
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "never" }],
      locale: { value: "en-US", pluralFoodHandling: "never" },
    } as any);
    const { parseIngredientText } = useIngredientTextParser();

    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tablespoons diced onion");
  });

  test("plural handling: 'without-unit' strategy uses plural food without unit", () => {
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "without-unit" }],
      locale: { value: "en-US", pluralFoodHandling: "without-unit" },
    } as any);
    const { parseIngredientText } = useIngredientTextParser();

    const ingredient = createRecipeIngredient({
      quantity: 2,
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
      unit: undefined,
    });

    expect(parseIngredientText(ingredient)).toEqual("2 diced onions");
  });

  test("plural handling: 'without-unit' strategy uses singular food with unit", () => {
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "without-unit" }],
      locale: { value: "en-US", pluralFoodHandling: "without-unit" },
    } as any);
    const { parseIngredientText } = useIngredientTextParser();

    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tablespoons diced onion");
  });

  test("decimal below minimum precision shows < 0.001", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.0001,
      unit: { id: "1", name: "cup", useAbbreviation: false },
      food: { id: "1", name: "salt" },
    });

    expect(parseIngredientText(ingredient)).toEqual("&lt; 0.001 cup salt");
  });

  test("fraction below minimum denominator shows < 1/10", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.05,
      unit: { id: "1", name: "cup", fraction: true, useAbbreviation: false },
      food: { id: "1", name: "salt" },
    });

    expect(parseIngredientText(ingredient)).toEqual("&lt; <sup>1</sup><span>⁄</span><sub>10</sub> cup salt");
  });

  test("fraction below minimum denominator without formatting shows < 1/10", () => {
    const ingredient = createRecipeIngredient({
      quantity: 0.05,
      unit: { id: "1", name: "cup", fraction: true, useAbbreviation: false },
      food: { id: "1", name: "salt" },
    });

    expect(parseIngredientText(ingredient, 1, false)).toEqual("&lt; 1/10 cup salt");
  });

  // Regression test for https://github.com/mealie-recipes/mealie/issues/7079
  // Unparsed ingredients (no food, no unit) store the full text in the note field.
  // When such an ingredient also has a quantity (e.g. from a forced-quantity setting),
  // parseIngredientText incorrectly prepends that quantity to the note, producing
  // strings like "1 1/2 cup apples" instead of the original "1/2 cup apples".
  // Callers constructing strings for the NLP parser should use the note directly
  // for unparsed ingredients instead of calling parseIngredientText.
  test("unparsed ingredient with quantity prepends quantity to note (issue #7079)", () => {
    const ingredient = createRecipeIngredient({
      quantity: 1,
      unit: undefined,
      food: undefined,
      note: "1/2 cup apples",
    });

    // This demonstrates the problematic behavior: parseIngredientText combines
    // the quantity field with the note, producing "1 1/2 cup apples"
    const result = parseIngredientText(ingredient, 1, false);
    expect(result).toEqual("1 1/2 cup apples");

    // The note alone contains the correct text for NLP parsing
    expect(ingredient.note).toEqual("1/2 cup apples");
  });
});
