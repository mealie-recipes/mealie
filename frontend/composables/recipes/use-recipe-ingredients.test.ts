import { describe, test, expect, vi, beforeEach } from "vitest";
import { parseIngredientText } from "./use-recipe-ingredients";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import { useLocales } from "../use-locales";

vi.mock("../use-locales");

describe(parseIngredientText.name, () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "always" }],
      locale: { value: "en-US", pluralFoodHandling: "always" },
    } as any);
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

    const ingredient = createRecipeIngredient({
      quantity: 2,
      unit: { id: "1", name: "tablespoon", pluralName: "tablespoons", useAbbreviation: false },
      food: { id: "1", name: "diced onion", pluralName: "diced onions" },
    });

    expect(parseIngredientText(ingredient)).toEqual("2 tablespoons diced onion");
  });
});
