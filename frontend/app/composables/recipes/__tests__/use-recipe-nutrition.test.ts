import { describe, expect, test } from "vitest";
import { parseNutritionValue } from "../use-recipe-nutrition";

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
