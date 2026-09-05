import { describe, expect, test } from "vitest";
import { makeWrapper } from "~/tests/utils";
import type { CreateIngredientUnit, RecipeIngredient } from "~/lib/api/types/recipe";
import { canConvertIngredient, useUnitConversion } from "../use-unit-conversion";

const { convertIngredient } = makeWrapper(() => useUnitConversion());

const ingredient = (quantity: number, unit: Partial<CreateIngredientUnit> | null): RecipeIngredient => ({
  quantity,
  food: { id: "1", name: "flour" },
  unit: unit === null ? null : { id: "1", name: "unit", ...unit },
});

/** An ingredient measured in whole grams, the simplest way to pin a base magnitude. */
const grams = (quantity: number) =>
  ingredient(quantity, { name: "gram", standardUnit: "gram", standardQuantity: 1 });

/** An ingredient measured in whole ounces — customary, so it converts when metric is asked for. */
const ounces = (quantity: number) =>
  ingredient(quantity, { name: "ounce", standardUnit: "ounce", standardQuantity: 1 });

/** An ingredient measured in whole millilitres. */
const millilitres = (quantity: number) =>
  ingredient(quantity, { name: "milliliter", standardUnit: "milliliter", standardQuantity: 1 });

describe("convertIngredient", () => {
  describe("ingredients that can't be converted", () => {
    const cases: [string, RecipeIngredient][] = [
      ["no unit", ingredient(1, null)],
      ["zero quantity", grams(0)],
      ["no standardUnit", ingredient(1, { name: "pinch" })],
      ["no standardQuantity", ingredient(1, { name: "gram", standardUnit: "gram" })],
      ["unrecognized standardUnit", ingredient(1, { name: "x", standardUnit: "furlong", standardQuantity: 1 })],
    ];

    test.each(cases)("%s is returned unchanged, with the same object identity", (_label, input) => {
      expect(canConvertIngredient(input)).toBe(false);
      expect(convertIngredient(input, "metric")).toBe(input);
    });
  });

  describe("choosing a rung", () => {
    test("stays on the smaller unit below the takeover point", () => {
      // 30oz is 850g, short of the kilogram rung
      const converted = convertIngredient(ounces(30), "metric");

      expect(converted.unit?.name).toBe("gram");
      expect(converted.quantity).toBeCloseTo(850.5, 1);
    });

    test("moves up once the takeover point is reached", () => {
      // 40oz is 1134g, past it
      const converted = convertIngredient(ounces(40), "metric");

      expect(converted.unit?.name).toBe("kilogram");
      expect(converted.quantity).toBeCloseTo(1.134, 3);
    });

    test("cups take over at a quarter cup rather than a whole one", () => {
      // a quarter cup is 59.147ml, so 59ml is still tablespoons and 60ml is cups
      expect(convertIngredient(millilitres(59), "us").unit?.name).toBe("tablespoon");
      expect(convertIngredient(millilitres(60), "us").unit?.name).toBe("cup");
    });

    test("falls back to the smallest rung below the whole ladder", () => {
      const converted = convertIngredient(millilitres(1), "us");

      expect(converted.unit?.name).toBe("teaspoon");
      expect(converted.quantity).toBeCloseTo(0.203, 3);
    });
  });

  describe("ingredients already in the reader's system", () => {
    const tablespoons = (quantity: number) =>
      ingredient(quantity, { name: "tbsp", standardUnit: "fluid_ounce", standardQuantity: 0.5 });

    test("customary units are untouched when a customary system is chosen", () => {
      // "4 tbsp" must not come back as "1/4 cup" — a lateral restatement, not a conversion
      const input = tablespoons(4);

      expect(convertIngredient(input, "us")).toBe(input);
    });

    test("metric units are untouched when metric is chosen", () => {
      const input = grams(1000);

      expect(convertIngredient(input, "metric")).toBe(input);
    });

    test("stays untouched when scaled, so the unit never changes under the reader", () => {
      const input = grams(1000);

      expect(convertIngredient(input, "metric", 10)).toBe(input);
    });

    test("but foreign units still convert", () => {
      expect(convertIngredient(tablespoons(4), "metric").unit?.name).toBe("milliliter");
      expect(convertIngredient(grams(1000), "us").unit?.name).toBe("pound");
    });
  });

  describe("scale", () => {
    // Spec §4.3: the rung comes from the scaled magnitude, but the quantity handed back is
    // unscaled, so existing `useParsedIngredientText(ingredient, scale)` call sites still work.
    test("picks the rung from the scaled magnitude", () => {
      expect(convertIngredient(ounces(4), "metric", 1).unit?.name).toBe("gram");
      expect(convertIngredient(ounces(4), "metric", 10).unit?.name).toBe("kilogram");
    });

    test("returns an unscaled quantity, so 4oz at 10x reads as 1.13kg", () => {
      const converted = convertIngredient(ounces(4), "metric", 10);

      expect(converted.quantity).toBeCloseTo(0.1134, 4);
      expect((converted.quantity as number) * 10).toBeCloseTo(1.134, 3);
    });
  });

  describe("dimensions never cross", () => {
    // "ounce" means fluid ounce often enough that UnitConverter rewrites it when merging with a
    // volume, but at display time there's no second unit to infer from and standardUnit has
    // already settled it. A mass ounce must stay on the mass ladder.
    test("a mass ounce converts to grams, not millilitres", () => {
      const ounces = ingredient(4, { name: "ounce", standardUnit: "ounce", standardQuantity: 1 });
      const converted = convertIngredient(ounces, "metric");

      expect(converted.unit?.name).toBe("gram");
      expect(converted.quantity).toBeCloseTo(113.4, 1);
    });

    test("a fluid ounce converts to millilitres", () => {
      const fluidOunces = ingredient(4, { name: "fl oz", standardUnit: "fluid_ounce", standardQuantity: 1 });
      const converted = convertIngredient(fluidOunces, "metric");

      expect(converted.unit?.name).toBe("milliliter");
      expect(converted.quantity).toBeCloseTo(118.3, 1);
    });
  });

  describe("the unit it hands back", () => {
    test("falls back to the singular abbreviation when the seed has no plural one", () => {
      // pound is the only seeded unit carrying a distinct plural abbreviation
      expect(convertIngredient(grams(500), "us").unit).toMatchObject({
        abbreviation: "lb",
        pluralAbbreviation: "lbs",
      });
      expect(convertIngredient(ounces(40), "metric").unit).toMatchObject({
        abbreviation: "kg",
        pluralAbbreviation: "kg",
      });
    });

    test("carries translated names and abbreviations", () => {
      const converted = convertIngredient(ounces(40), "metric");

      expect(converted.unit).toMatchObject({
        name: "kilogram",
        pluralName: "kilograms",
        abbreviation: "kg",
        pluralAbbreviation: "kg",
      });
    });

    test("renders metric as decimals and customary as fractions", () => {
      expect(convertIngredient(ounces(4), "metric").unit?.fraction).toBe(false);
      expect(convertIngredient(grams(100), "us").unit?.fraction).toBe(true);
    });

    test("preserves whether the recipe's own unit was abbreviated", () => {
      const abbreviated = ingredient(100, {
        name: "gram",
        standardUnit: "gram",
        standardQuantity: 1,
        useAbbreviation: true,
      });

      expect(convertIngredient(abbreviated, "us").unit?.useAbbreviation).toBe(true);
      expect(convertIngredient(grams(100), "us").unit?.useAbbreviation).toBeFalsy();
    });

    test("drops the source unit's identity and standardization data", () => {
      const converted = convertIngredient(grams(100), "us");

      expect(converted.unit?.id).toBeUndefined();
      expect(converted.unit?.standardUnit).toBeUndefined();
      expect(converted.unit?.standardQuantity).toBeUndefined();
    });
  });

  test("leaves the rest of the ingredient alone", () => {
    const input = { ...grams(100), note: "sifted", referenceId: "abc" };
    const converted = convertIngredient(input, "us");

    expect(converted.note).toBe("sifted");
    expect(converted.referenceId).toBe("abc");
    expect(converted.food).toBe(input.food);
    expect(converted).not.toBe(input);
  });
});
