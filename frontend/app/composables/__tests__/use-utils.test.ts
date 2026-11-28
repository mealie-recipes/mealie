import { describe, expect, test } from "vitest";
import { findHttpUrl, normalize, normalizeFilter } from "../use-utils";

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
    const patternA = "Escargots persillés";
    const patternB = "persillés";

    expect(normalizeFilter(patternA, patternB)).toBeTruthy();
    expect(normalizeFilter(patternB, patternA)).toBeFalsy();
  });
  test("normalize", () => {
    const value = "Cœur de bœuf";
    const query = "coeur";
    expect(normalizeFilter(value, query)).toBeTruthy();
  });
});

describe("test findHttpUrl", () => {
  test("text is only a URL", () => {
    expect(findHttpUrl("https://fooby.ch/de/rezepte/16252/")).toEqual("https://fooby.ch/de/rezepte/16252/");
  });
  test("URL after a title on a new line", () => {
    expect(findHttpUrl("Schau mal: Spaghetti aglio e olio\nhttps://fooby.ch/de/rezepte/16252/"))
      .toEqual("https://fooby.ch/de/rezepte/16252/");
  });
  test("URL between other words", () => {
    expect(findHttpUrl("Try this http://example.com/recipe tonight")).toEqual("http://example.com/recipe");
  });
  test("first URL wins", () => {
    expect(findHttpUrl("https://a.example/1 https://b.example/2")).toEqual("https://a.example/1");
  });
  test("no URL", () => {
    expect(findHttpUrl("Spaghetti aglio e olio")).toBeNull();
    expect(findHttpUrl("")).toBeNull();
  });
  test("other protocols are ignored", () => {
    expect(findHttpUrl("mailto:chef@example.com ftp://example.com/file")).toBeNull();
  });
});
