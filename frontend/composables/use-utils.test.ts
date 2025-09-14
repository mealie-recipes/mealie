import { describe, expect, test } from "vitest";
import { normalize, normalizeFilter } from "./use-utils";

describe("test normalize", () => {
  test("base case", () => {
    expect(normalize("banana")).not.toEqual(normalize("Potatoes"));
  });
  test("diacritics", () => {
    expect(normalize("Rátàtôuile")).toEqual("ratatouile");
  });
  test("ligatures", () => {
    expect(normalize("Ĳ")).toEqual("ij");
    expect(normalize("æ")).toEqual("ae");
    expect(normalize("œ")).toEqual("oe");
    expect(normalize("ﬀ")).toEqual("ff");
    expect(normalize("ﬁ")).toEqual("fi");
    expect(normalize("ﬆ")).toEqual("st");
  });
});

describe("test normalize filter", () => {
  test("base case", () => {
    const patern_a = "Escargots persillés";
    const patern_b = "persillés";

    expect(normalizeFilter(patern_a, patern_b)).toBeTruthy();
    expect(normalizeFilter(patern_b, patern_a)).toBeFalsy();
  });
  test("normalize", () => {
    const value = "Cœur de bœuf";
    const query = "coeur";
    expect(normalizeFilter(value, query)).toBeTruthy();
  });
});
