import { describe, expect, test } from "vitest";
import { useExtractIngredientReferences } from "./use-extract-ingredient-references";

const punctuationMarks = ["*", "?", "/", "!", "**", "&", "."];

describe("test use extract ingredient references", () => {
  test("when text empty return empty", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "", true);
    expect(result).toStrictEqual(new Set());
  });

  test("when and ingredient matches exactly and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onion", true);

    expect(result).toEqual(new Set(["123"]));
  });

  test.each(punctuationMarks)("when ingredient is suffixed by punctuation, return the referenceId", (suffix) => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onion" + suffix, true);

    expect(result).toEqual(new Set(["123"]));
  });

  test.each(punctuationMarks)("when ingredient is prefixed by punctuation, return the referenceId", (prefix) => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing " + prefix + "Onion", true);
    expect(result).toEqual(new Set(["123"]));
  });

  test("when ingredient is first on a multiline, return the referenceId", () => {
    const multilineSting = "lksjdlk\nOnion";
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], multilineSting, true);
    expect(result).toEqual(new Set(["123"]));
  });

  test("when the ingredient matches partially exactly and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onions", true);
    expect(result).toEqual(new Set(["123"]));
  });

  test("when the ingredient matches with different casing and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing oNions", true);
    expect(result).toEqual(new Set(["123"]));
  });

  test("when no ingredients, return empty", () => {
    const result = useExtractIngredientReferences([], [], "A sentence containing oNions", true);
    expect(result).toEqual(new Set());
  });

  test("when and ingredient matches but in the existing referenceIds, do not return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onion", referenceId: "123" }], ["123"], "A sentence containing Onion", true);

    expect(result).toEqual(new Set());
  });

  test("when an word is 2 letter of shorter, it is ignored", () => {
    const result = useExtractIngredientReferences([{ note: "Onion", referenceId: "123" }], [], "A sentence containing On", true);

    expect(result).toEqual(new Set());
  });
});
