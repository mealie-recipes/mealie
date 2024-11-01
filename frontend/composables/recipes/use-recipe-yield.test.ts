import { describe, expect, test } from "vitest";
import { useRecipeYield } from "./use-recipe-yield";

describe("test use recipe yield", () => {
  function asFrac(numerator: number, denominator: number): string {
    return `<sup>${numerator}</sup><span>&frasl;</span><sub>${denominator}</sub>`;
  }

  test("base case", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(3, "total servings");
    expect(yieldQuantity).toStrictEqual(3);
    expect(yieldString).toStrictEqual("total servings");
    expect(yieldDisplay).toStrictEqual("3 total servings");
  });

  test("base case scaled", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(3, "servings", 2);
    expect(yieldQuantity).toStrictEqual(6);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual("6 servings");
  });

  test("zero scale", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(3, "servings", 0);
    expect(yieldQuantity).toStrictEqual(0);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual("servings");
  });

  test("numbers in string", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(3, "servings or 4 servings", 2);
    expect(yieldQuantity).toStrictEqual(6);
    expect(yieldString).toStrictEqual("servings or 4 servings");
    expect(yieldDisplay).toStrictEqual("6 servings or 4 servings");
  });

  test("fraction in string", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(3, "servings or 1/2 servings", 2);
    expect(yieldQuantity).toStrictEqual(6);
    expect(yieldString).toStrictEqual("servings or 1/2 servings");
    expect(yieldDisplay).toStrictEqual("6 servings or 1/2 servings");
  });

  test("zero quantity", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(0, "servings");
    expect(yieldQuantity).toStrictEqual(0);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual("servings");
  });

  test("zero quantity with whitespace", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(0, "servings");
    expect(yieldQuantity).toStrictEqual(0);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual("servings");
  });

  test("quantity only", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(2, "");
    expect(yieldQuantity).toStrictEqual(2);
    expect(yieldString).toStrictEqual("");
    expect(yieldDisplay).toStrictEqual("2");
  });

  test("basic fraction", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(0.5, "servings");
    expect(yieldQuantity).toStrictEqual(0.5);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`${asFrac(1, 2)} servings`);
  });

  test("mixed fraction", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(1.5, "servings");
    expect(yieldQuantity).toStrictEqual(1.5);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`1${asFrac(1, 2)} servings`);
  });

  test("mixed fraction scaled", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(1.5, "servings", 9);
    expect(yieldQuantity).toStrictEqual(13.5);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`13${asFrac(1, 2)} servings`);
  });

  test("small scale", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(1, "servings", 0.125);
    expect(yieldQuantity).toStrictEqual(0.125);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`${asFrac(1, 8)} servings`);
  });

  test("small qty", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(0.125, "servings");
    expect(yieldQuantity).toStrictEqual(0.125);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`${asFrac(1, 8)} servings`);
  });

  test("rounded decimal", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(1.3344556677889999999, "servings");
    expect(yieldQuantity).toStrictEqual(1.334);
    expect(yieldString).toStrictEqual("servings");
    expect(yieldDisplay).toStrictEqual(`1${asFrac(1, 3)} servings`);
  });

  test("preserve HTML", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(0.5, "<b>servings</b>");
    expect(yieldQuantity).toStrictEqual(.5);
    expect(yieldString).toStrictEqual("<b>servings</b>");
    expect(yieldDisplay).toStrictEqual(`${asFrac(1, 2)} <b>servings</b>`);
  });

  test("sanitize HTML", () => {
    const { yieldQuantity, yieldString, yieldDisplay } = useRecipeYield(
      0.5, "<iframe><script>servings</script></iframe>"
    );
    expect(yieldQuantity).toStrictEqual(.5);
    expect(yieldString).toStrictEqual("");
    expect(yieldDisplay).toStrictEqual(asFrac(1, 2));
  });
});
