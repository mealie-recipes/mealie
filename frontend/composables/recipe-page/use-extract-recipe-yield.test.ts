import { describe, expect, test } from "vitest";
import { useExtractRecipeYield } from "./use-extract-recipe-yield";

describe("test use extract recipe yield", () => {
    test("when text empty return empty", () => {
        const result = useExtractRecipeYield(null, 1);
        expect(result).toStrictEqual("");
    });

    test("when text matches nothing return text", () => {
        const val = "this won't match anything";
        const result = useExtractRecipeYield(val, 1);
        expect(result).toStrictEqual(val);

        const resultScaled = useExtractRecipeYield(val, 5);
        expect(resultScaled).toStrictEqual(val);
    });

    test("when text matches a mixed fraction, return a scaled fraction", () => {
        const val = "10 1/2 units";
        const result = useExtractRecipeYield(val, 1);
        expect(result).toStrictEqual(val);

        const resultScaled = useExtractRecipeYield(val, 3);
        expect(resultScaled).toStrictEqual("31 1/2 units");

        const resultScaledPartial = useExtractRecipeYield(val, 2.5);
        expect(resultScaledPartial).toStrictEqual("26 1/4 units");

        const resultScaledInt = useExtractRecipeYield(val, 4);
        expect(resultScaledInt).toStrictEqual("42 units");
    });

    test("when text matches a fraction, return a scaled fraction", () => {
        const val = "1/3 plates";
        const result = useExtractRecipeYield(val, 1);
        expect(result).toStrictEqual(val);

        const resultScaled = useExtractRecipeYield(val, 2);
        expect(resultScaled).toStrictEqual("2/3 plates");

        const resultScaledInt = useExtractRecipeYield(val, 3);
        expect(resultScaledInt).toStrictEqual("1 plates");

        const resultScaledPartial = useExtractRecipeYield(val, 2.5);
        expect(resultScaledPartial).toStrictEqual("5/6 plates");

        const resultScaledMixed = useExtractRecipeYield(val, 4);
        expect(resultScaledMixed).toStrictEqual("1 1/3 plates");
    });

    test("when text matches a decimal, return a scaled, rounded decimal", () => {
        const val = "1.25 parts";
        const result = useExtractRecipeYield(val, 1);
        expect(result).toStrictEqual(val);

        const resultScaled = useExtractRecipeYield(val, 2);
        expect(resultScaled).toStrictEqual("2.5 parts");

        const resultScaledInt = useExtractRecipeYield(val, 4);
        expect(resultScaledInt).toStrictEqual("5 parts");

        const resultScaledPartial = useExtractRecipeYield(val, 2.5);
        expect(resultScaledPartial).toStrictEqual("3.125 parts");

        const roundedVal = "1.33333333333333333333 parts";
        const resultScaledRounded = useExtractRecipeYield(roundedVal, 2);
        expect(resultScaledRounded).toStrictEqual("2.667 parts");
    });

    test("when text matches an int, return a scaled int", () => {
        const val = "5 bowls";
        const result = useExtractRecipeYield(val, 1);
        expect(result).toStrictEqual(val);

        const resultScaled = useExtractRecipeYield(val, 2);
        expect(resultScaled).toStrictEqual("10 bowls");

        const resultScaledPartial = useExtractRecipeYield(val, 2.5);
        expect(resultScaledPartial).toStrictEqual("12.5 bowls");

        const resultScaledLarge = useExtractRecipeYield(val, 10);
        expect(resultScaledLarge).toStrictEqual("50 bowls");
    });

    test("when text contains an invalid fraction, return the original string", () => {
        const valDivZero = "3/0 servings";
        const resultDivZero = useExtractRecipeYield(valDivZero, 3);
        expect(resultDivZero).toStrictEqual(valDivZero);

        const valDivZeroMixed = "2 4/0 servings";
        const resultDivZeroMixed = useExtractRecipeYield(valDivZeroMixed, 6);
        expect(resultDivZeroMixed).toStrictEqual(valDivZeroMixed);
    });

    test("when text contains a weird or small fraction, return the original string", () => {
        const valWeird = "2323231239087/134527431962272135 servings";
        const resultWeird = useExtractRecipeYield(valWeird, 5);
        expect(resultWeird).toStrictEqual(valWeird);

        const valSmall = "1/20230225 lovable servings";
        const resultSmall = useExtractRecipeYield(valSmall, 12);
        expect(resultSmall).toStrictEqual(valSmall);
    });

    test("when text contains multiple numbers, the first is parsed as the servings amount", () => {
        const val = "100 sets of 55 bowls";
        const result = useExtractRecipeYield(val, 3);
        expect(result).toStrictEqual("300 sets of 55 bowls");
    })
});
