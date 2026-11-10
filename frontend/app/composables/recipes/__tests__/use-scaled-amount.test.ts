import { describe, expect, test } from "vitest";
import { calculateScaleFromYield, useScaledAmount } from "../use-scaled-amount";

describe("test use recipe yield", () => {
  function asFrac(numerator: number, denominator: number): string {
    return `<sup>${numerator}</sup><span>&frasl;</span><sub>${denominator}</sub>`;
  }

  test("base case", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(3);
    expect(scaledAmount).toStrictEqual(3);
    expect(scaledAmountDisplay).toStrictEqual("3");
  });

  test("base case scaled", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(3, 2);
    expect(scaledAmount).toStrictEqual(6);
    expect(scaledAmountDisplay).toStrictEqual("6");
  });

  test("zero scale", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(3, 0);
    expect(scaledAmount).toStrictEqual(0);
    expect(scaledAmountDisplay).toStrictEqual("");
  });

  test("zero quantity", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(0);
    expect(scaledAmount).toStrictEqual(0);
    expect(scaledAmountDisplay).toStrictEqual("");
  });

  test("basic fraction", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(0.5);
    expect(scaledAmount).toStrictEqual(0.5);
    expect(scaledAmountDisplay).toStrictEqual(asFrac(1, 2));
  });

  test("mixed fraction", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(1.5);
    expect(scaledAmount).toStrictEqual(1.5);
    expect(scaledAmountDisplay).toStrictEqual(`1${asFrac(1, 2)}`);
  });

  test("mixed fraction scaled", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(1.5, 9);
    expect(scaledAmount).toStrictEqual(13.5);
    expect(scaledAmountDisplay).toStrictEqual(`13${asFrac(1, 2)}`);
  });

  test("small scale", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(1, 0.125);
    expect(scaledAmount).toStrictEqual(0.125);
    expect(scaledAmountDisplay).toStrictEqual(asFrac(1, 8));
  });

  test("small qty", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(0.125);
    expect(scaledAmount).toStrictEqual(0.125);
    expect(scaledAmountDisplay).toStrictEqual(asFrac(1, 8));
  });

  test("rounded decimal", () => {
    const { scaledAmount, scaledAmountDisplay } = useScaledAmount(1.3344559997);
    expect(scaledAmount).toStrictEqual(1.334);
    expect(scaledAmountDisplay).toStrictEqual(`1${asFrac(1, 3)}`);
  });
});

describe("calculateScaleFromYield", () => {
  test.each([
    [8, 4, 2],
    [2, 4, 0.5],
    [4, 4, 1],
    [1, 3, 1 / 3],
    [0.5, 1, 0.5],
  ])("a yield of %d from %d servings is a scale of %d", (newYield, recipeServings, expected) => {
    expect(calculateScaleFromYield(newYield, recipeServings)).toBeCloseTo(expected);
  });

  test.each([0, -1, NaN])("keeps the current scale for an unusable yield of %d", (newYield) => {
    expect(calculateScaleFromYield(newYield, 4)).toBeNull();
  });

  test.each([0, -2])("falls back to unscaled when the recipe has %d servings", (recipeServings) => {
    expect(calculateScaleFromYield(6, recipeServings)).toStrictEqual(1);
  });

  test("round-trips with the scaled amount shown to the user", () => {
    const scale = calculateScaleFromYield(5, 3)!;
    expect(useScaledAmount(3, scale).scaledAmount).toStrictEqual(5);
  });
});
