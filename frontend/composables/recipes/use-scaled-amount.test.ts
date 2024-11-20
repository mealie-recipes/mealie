import { describe, expect, test } from "vitest";
import { useScaledAmount } from "./use-scaled-amount";

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
