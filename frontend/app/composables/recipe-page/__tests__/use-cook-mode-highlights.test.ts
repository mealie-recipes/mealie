import { describe, expect, test } from "vitest";
import { highlightTerms, ingredientHighlightTerms } from "../use-cook-mode-highlights";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

const hl = (text: string) => `<span class="cook-hl">${text}</span>`;

describe("highlightTerms", () => {
  test("wraps whole-word mentions, ignoring case", () => {
    expect(highlightTerms("Add the Onion and onions.", ["onion"])).toBe(`Add the ${hl("Onion")} and ${hl("onions")}.`);
  });

  test("does not match inside other words", () => {
    expect(highlightTerms("Add the scallions", ["scallion", "lion"])).toBe(`Add the ${hl("scallions")}`);
    expect(highlightTerms("Season with oregano", ["egg"])).toBe("Season with oregano");
  });

  test("prefers the longest term", () => {
    expect(highlightTerms("Slice the red pepper", ["pepper", "red pepper"])).toBe(`Slice the ${hl("red pepper")}`);
  });

  test("leaves links, code and html alone", () => {
    const source = "Use [garlic press](https://example.com/garlic) on the garlic, see `garlic` and <b title=\"garlic\">x</b>";
    expect(highlightTerms(source, ["garlic"])).toBe(
      `Use [garlic press](https://example.com/garlic) on the ${hl("garlic")}, see \`garlic\` and <b title="garlic">x</b>`,
    );
  });

  test("escapes terms", () => {
    expect(highlightTerms("Add (a) chili+lime salt", ["chili+lime"])).toBe(`Add (a) ${hl("chili+lime")} salt`);
  });

  test("returns the source without terms", () => {
    expect(highlightTerms("Stir well", [])).toBe("Stir well");
  });
});

describe("ingredientHighlightTerms", () => {
  test("uses food names and their last word", () => {
    const ingredients: RecipeIngredient[] = [
      { food: { id: "1", name: "yellow onion", pluralName: "yellow onions" } },
      { food: { id: "2", name: "garlic" } },
    ];
    expect(ingredientHighlightTerms(ingredients, "Add the onion and garlic")).toEqual(
      expect.arrayContaining(["yellow onion", "onion", "yellow onions", "onions", "garlic"]),
    );
  });

  test("falls back to words an unparsed ingredient shares with the step", () => {
    const ingredients: RecipeIngredient[] = [{ note: "2 large eggs, beaten" }];
    expect(ingredientHighlightTerms(ingredients, "Crack the eggs into a large bowl")).toEqual(["eggs"]);
  });
});
