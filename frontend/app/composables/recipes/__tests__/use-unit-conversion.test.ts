import { describe, expect, test } from "vitest";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";
import {
  convertIngredient,
  convertTemperatures,
  resolveTemperatureTarget,
  type DisplayUnitKey,
  type UnitNameResolver,
} from "../use-unit-conversion";

// The pure functions take the name resolver as an argument, so the tests can skip i18n
// entirely and assert on the unit key that was picked.
const resolveName: UnitNameResolver = key => ({
  name: key,
  pluralName: `${key}s`,
  abbreviation: key,
  pluralAbbreviation: key,
});

function ingredient(quantity: number, standardUnit: string | null, standardQuantity: number | null): RecipeIngredient {
  return {
    quantity,
    food: { id: "food-1", name: "Flour" },
    unit: standardUnit
      ? { id: "unit-1", name: "authored unit", standardUnit, standardQuantity }
      : { id: "unit-1", name: "authored unit" },
  } as RecipeIngredient;
}

function convert(ing: RecipeIngredient, system: UnitSystem, scale = 1) {
  const result = convertIngredient(ing, system, scale, resolveName);
  return { key: result.unit?.name as DisplayUnitKey, quantity: result.quantity as number, unit: result.unit };
}

describe("convertIngredient — mass", () => {
  test.each<[string, number, string, UnitSystem, DisplayUnitKey, number]>([
    ["pound to metric stays under a kilo", 1, "pound", "metric", "gram", 453.59237],
    ["three pounds cross into kilograms", 3, "pound", "metric", "kilogram", 1.36077711],
    ["a pinch drops to milligrams", 0.5, "gram", "metric", "milligram", 500],
    ["grams to US above a pound", 500, "gram", "us", "pound", 1.1023113109243878],
    ["grams to US below a pound", 100, "gram", "us", "ounce", 3.5273961949580412],
    ["imperial shares US mass units", 500, "gram", "imperial", "pound", 1.1023113109243878],
  ])("%s", (_name, quantity, standardUnit, system, expectedKey, expectedQuantity) => {
    const { key, quantity: converted } = convert(ingredient(quantity, standardUnit, 1), system);
    expect(key).toBe(expectedKey);
    expect(converted).toBeCloseTo(expectedQuantity, 6);
  });

  test("exactly one kilogram is a kilogram, one gram short is not", () => {
    expect(convert(ingredient(1000, "gram", 1), "metric").key).toBe("kilogram");
    expect(convert(ingredient(999, "gram", 1), "metric").key).toBe("gram");
  });
});

describe("convertIngredient — volume", () => {
  test.each<[string, number, string, UnitSystem, DisplayUnitKey, number]>([
    ["cups to metric millilitres", 2, "cup", "metric", "milliliter", 473.176473],
    ["cups to metric litres", 5, "cup", "metric", "liter", 1.1829411825],
    ["millilitres to US cups", 200, "milliliter", "us", "cup", 0.8453506979638029],
    ["millilitres to US tablespoons", 30, "milliliter", "us", "tablespoon", 2.028841362132],
    ["millilitres to US teaspoons", 5, "milliliter", "us", "teaspoon", 1.014420681066],
    ["imperial keeps small volumes in millilitres", 200, "milliliter", "imperial", "milliliter", 200],
    ["imperial reaches for the pint", 1000, "milliliter", "imperial", "imperial-pint", 1.7597539863927023],
  ])("%s", (_name, quantity, standardUnit, system, expectedKey, expectedQuantity) => {
    const { key, quantity: converted } = convert(ingredient(quantity, standardUnit, 1), system);
    expect(key).toBe(expectedKey);
    expect(converted).toBeCloseTo(expectedQuantity, 6);
  });

  test("a seeded teaspoon (1/6 fluid ounce) round-trips through metric", () => {
    const { key, quantity } = convert(ingredient(1, "fluid_ounce", 1 / 6), "metric");
    expect(key).toBe("milliliter");
    expect(quantity).toBeCloseTo(4.92892159375, 6);
  });
});

describe("convertIngredient — scale awareness", () => {
  test("the display unit follows the scaled magnitude, the quantity does not", () => {
    // 100 g at 10x is a kilogram of flour; the quantity stays unscaled so the ingredient
    // can still be passed to useParsedIngredientText(ingredient, scale).
    const { key, quantity } = convert(ingredient(100, "gram", 1), "metric", 10);
    expect(key).toBe("kilogram");
    expect(quantity).toBeCloseTo(0.1, 6);
    expect(quantity * 10).toBeCloseTo(1, 6);
  });

  test("scaling down keeps the smaller unit", () => {
    expect(convert(ingredient(1, "kilogram", 1), "metric", 0.5).key).toBe("gram");
  });
});

describe("convertIngredient — passthrough", () => {
  const cases: [string, RecipeIngredient][] = [
    ["no unit at all", { quantity: 2, food: { id: "f", name: "Eggs" } } as RecipeIngredient],
    ["unit without standardisation", ingredient(2, null, null)],
    ["unit with a standard unit but no quantity factor", ingredient(2, "gram", null)],
    ["zero quantity", ingredient(0, "gram", 1)],
    ["unrecognised standard unit", ingredient(2, "furlong", 1)],
  ];

  test.each(cases)("returns the ingredient untouched: %s", (_name, ing) => {
    expect(convertIngredient(ing, "metric", 1, resolveName)).toBe(ing);
  });

  test("the original system is a no-op", () => {
    const ing = ingredient(2, "cup", 1);
    expect(convertIngredient(ing, "original", 1, resolveName)).toBe(ing);
  });

  test("does not mutate the ingredient it was given", () => {
    const ing = ingredient(2, "cup", 1);
    convertIngredient(ing, "metric", 1, resolveName);
    expect(ing.quantity).toBe(2);
    expect(ing.unit?.name).toBe("authored unit");
  });
});

describe("convertIngredient — rendering hints", () => {
  test("metric units render as decimals, customary ones as fractions", () => {
    expect(convert(ingredient(2, "cup", 1), "metric").unit?.fraction).toBe(false);
    expect(convert(ingredient(200, "milliliter", 1), "us").unit?.fraction).toBe(true);
  });

  test("converted units are abbreviated", () => {
    expect(convert(ingredient(2, "cup", 1), "metric").unit?.useAbbreviation).toBe(true);
  });
});

describe("convertTemperatures", () => {
  test.each([
    ["Bake at 350°F for 30 minutes", "C", "Bake at 177°C for 30 minutes"],
    ["Bake at 350 °F", "C", "Bake at 177°C"],
    ["Bake at 350F", "C", "Bake at 177°C"],
    ["Bake at 350 F", "C", "Bake at 177°C"],
    ["Roast at 350-375°F", "C", "Roast at 177-191°C"],
    ["Roast at 350 – 375 °F", "C", "Roast at 177-191°C"],
    ["Preheat to 180°C", "F", "Preheat to 356°F"],
    ["Preheat to 176.7°C", "F", "Preheat to 350.1°F"],
    ["Bake at 350°f", "C", "Bake at 177°C"],
    // Plenty of recipe sites spell the unit out rather than using the degree sign.
    ["Bake at 425 degrees F", "C", "Bake at 218°C"],
    ["Bake at 425 degrees Fahrenheit", "C", "Bake at 218°C"],
    ["Preheat to 200 degrees Celsius", "F", "Preheat to 392°F"],
    ["Preheat to 200 degrees C", "F", "Preheat to 392°F"],
    ["Bake at 425 deg F", "C", "Bake at 218°C"],
    ["Bake at 425 deg. F", "C", "Bake at 218°C"],
    ["Bake at 425degrees F", "C", "Bake at 218°C"],
    ["Bake at 425 degrees f", "C", "Bake at 218°C"],
    ["Roast at 400-425 degrees F", "C", "Roast at 204-218°C"],
    ["Preheat to 200 degrees centigrade", "F", "Preheat to 392°F"],
  ])("%s -> %s", (input, target, expected) => {
    expect(convertTemperatures(input, target as "F" | "C")).toBe(expected);
  });

  test.each([
    ["already in the target unit", "Bake at 180°C", "C"],
    ["a vitamin, not a temperature", "Rich in vitamin C", "C"],
    ["a word starting with F", "Bake at 350Free", "C"],
    // "c" is the seeded abbreviation for cup — without the uppercase requirement these
    // would silently become 2°C and 35.6°F.
    ["a bare cup abbreviation", "Add 2 c water", "C"],
    ["a fractional cup abbreviation", "Add 1/2 c sugar", "F"],
    ["a bare cup abbreviation into Fahrenheit", "Add 2 c water", "F"],
    // "425 degrees" with no unit is Fahrenheit in a US recipe and Celsius in a European one.
    // Nothing in the text distinguishes them, so it is left as written.
    ["a bare degree count", "Bake at 425 degrees", "C"],
    ["a bare degree count into Fahrenheit", "Preheat to 200 degrees", "F"],
    ["a rotation, not a temperature", "Turn the dough 90 degrees", "C"],
  ])("leaves %s alone", (_name, input, target) => {
    expect(convertTemperatures(input, target as "F" | "C")).toBe(input);
  });

  test("a degree sign makes a lowercase unit unambiguous", () => {
    expect(convertTemperatures("Chill to 4°c", "F")).toBe("Chill to 39°F");
  });

  test("returns an empty string for empty input and passes through a null target", () => {
    expect(convertTemperatures("", "C")).toBe("");
    expect(convertTemperatures(null, "C")).toBe("");
    expect(convertTemperatures("Bake at 350°F", null)).toBe("Bake at 350°F");
  });

  test("converts several temperatures in one step", () => {
    expect(convertTemperatures("Start at 450°F, then drop to 350°F", "C"))
      .toBe("Start at 232°C, then drop to 177°C");
  });
});

describe("resolveTemperatureTarget", () => {
  test.each<[UnitSystem, TemperatureUnit, "F" | "C" | null]>([
    ["original", "system", null],
    ["metric", "system", "C"],
    ["imperial", "system", "C"],
    ["us", "system", "F"],
    // An explicit choice wins over the unit system — grams with a Fahrenheit oven is a
    // real combination, and it is the objection raised in discussion #3881.
    ["metric", "fahrenheit", "F"],
    ["us", "celsius", "C"],
    ["original", "celsius", "C"],
  ])("%s + %s -> %s", (system, preference, expected) => {
    expect(resolveTemperatureTarget(system, preference)).toBe(expected);
  });
});
