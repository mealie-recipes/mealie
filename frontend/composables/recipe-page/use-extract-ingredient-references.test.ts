import { describe, expect, test, vi, beforeEach } from "vitest";
import { useExtractIngredientReferences } from "./use-extract-ingredient-references";
import { useLocales } from "../use-locales";

vi.mock("../use-locales");

const punctuationMarks = ["*", "?", "/", "!", "**", "&", "."];

describe("test use extract ingredient references", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "without-unit" }],
      locale: { value: "en-US", pluralFoodHandling: "without-unit" },
    } as any);
  });

  test("when text empty return empty", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "");
    expect(result).toStrictEqual(new Set());
  });

  test("when and ingredient matches exactly and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onion");

    expect(result).toEqual(new Set(["123"]));
  });

  test.each(punctuationMarks)("when ingredient is suffixed by punctuation, return the referenceId", (suffix) => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onion" + suffix);

    expect(result).toEqual(new Set(["123"]));
  });

  test.each(punctuationMarks)("when ingredient is prefixed by punctuation, return the referenceId", (prefix) => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing " + prefix + "Onion");
    expect(result).toEqual(new Set(["123"]));
  });

  test("when ingredient is first on a multiline, return the referenceId", () => {
    const multilineSting = "lksjdlk\nOnion";
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], multilineSting);
    expect(result).toEqual(new Set(["123"]));
  });

  test("when the ingredient matches partially exactly and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing Onions");
    expect(result).toEqual(new Set(["123"]));
  });

  test("when the ingredient matches with different casing and has a reference id, return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onions", referenceId: "123" }], [], "A sentence containing oNions");
    expect(result).toEqual(new Set(["123"]));
  });

  test("when no ingredients, return empty", () => {
    const result = useExtractIngredientReferences([], [], "A sentence containing oNions");
    expect(result).toEqual(new Set());
  });

  test("when and ingredient matches but in the existing referenceIds, do not return the referenceId", () => {
    const result = useExtractIngredientReferences([{ note: "Onion", referenceId: "123" }], ["123"], "A sentence containing Onion");

    expect(result).toEqual(new Set());
  });

  test("when an word is 2 letter of shorter, it is ignored", () => {
    const result = useExtractIngredientReferences([{ note: "Onion", referenceId: "123" }], [], "A sentence containing On");

    expect(result).toEqual(new Set());
  });
});
