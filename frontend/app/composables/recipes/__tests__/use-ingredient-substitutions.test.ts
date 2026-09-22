import { ref } from "vue";
import { describe, expect, test } from "vitest";
import { ingredientSubstitutionSummary, substitutionFoodName, useIngredientSubstitutions } from "../use-ingredient-substitutions";
import type { IngredientFood, IngredientFoodSummary, RecipeIngredient } from "~/lib/api/types/recipe";

const broth: IngredientFoodSummary = { id: "broth-id", name: "Chicken broth" };
const pork: IngredientFoodSummary = { id: "pork-id", name: "Pork" };
const shallot: IngredientFoodSummary = { id: "shallot-id", name: "Shallot", pluralName: "Shallots" };

/** A food carrying its own substitutions, i.e. the ones that apply everywhere it is used. */
function foodWithSubstitutions(): IngredientFood {
  return {
    id: "stock-id",
    name: "Chicken stock",
    substitutions: [{ substituteFoodId: broth.id, substituteFood: broth }],
  };
}

describe("substitutionFoodName", () => {
  test("inflects with the line the substitute stands in for", () => {
    const substitution = { substituteFoodId: shallot.id, substituteFood: shallot };

    expect(substitutionFoodName(substitution, true)).toStrictEqual("Shallots");
    expect(substitutionFoodName(substitution, false)).toStrictEqual("Shallot");
  });

  test("falls back to the one name a food without a plural form has", () => {
    expect(substitutionFoodName({ substituteFoodId: broth.id, substituteFood: broth }, true)).toStrictEqual("Chicken broth");
  });

  test("is empty for a substitution that is only a note", () => {
    expect(substitutionFoodName({ note: "pork works" }, true)).toStrictEqual("");
  });
});

describe("useIngredientSubstitutions", () => {
  test("keeps the two tiers apart", () => {
    const ingredient: RecipeIngredient = {
      food: foodWithSubstitutions(),
      substitutions: [{ substituteFoodId: pork.id, substituteFood: pork }],
    };

    const { recipeSubstitutions, foodSubstitutions, hasSubstitutions } = useIngredientSubstitutions(() => ingredient);

    expect(recipeSubstitutions.value).toHaveLength(1);
    expect(recipeSubstitutions.value[0]?.substituteFood?.name).toStrictEqual("Pork");
    expect(foodSubstitutions.value).toHaveLength(1);
    expect(foodSubstitutions.value[0]?.substituteFood?.name).toStrictEqual("Chicken broth");
    expect(hasSubstitutions.value).toStrictEqual(true);
  });

  test("either tier alone still counts as having substitutions", () => {
    const recipeOnly = useIngredientSubstitutions(() => ({ substitutions: [{ note: "pork works" }] }));
    expect(recipeOnly.hasSubstitutions.value).toStrictEqual(true);
    expect(recipeOnly.foodSubstitutions.value).toStrictEqual([]);

    const foodOnly = useIngredientSubstitutions(() => ({ food: foodWithSubstitutions() }));
    expect(foodOnly.hasSubstitutions.value).toStrictEqual(true);
    expect(foodOnly.recipeSubstitutions.value).toStrictEqual([]);
  });

  test("an ingredient with no food and no substitutions has none", () => {
    const { recipeSubstitutions, foodSubstitutions, hasSubstitutions } = useIngredientSubstitutions(() => ({}));

    expect(recipeSubstitutions.value).toStrictEqual([]);
    expect(foodSubstitutions.value).toStrictEqual([]);
    expect(hasSubstitutions.value).toStrictEqual(false);
  });

  test("a food that carries no substitutions contributes none", () => {
    const { foodSubstitutions, hasSubstitutions } = useIngredientSubstitutions(() => ({
      food: { id: "stock-id", name: "Chicken stock" },
    }));

    expect(foodSubstitutions.value).toStrictEqual([]);
    expect(hasSubstitutions.value).toStrictEqual(false);
  });

  test("tracks the ingredient it was given", () => {
    // the composable takes a getter rather than a value so a row that swaps ingredients
    // re-reads them instead of holding the first one it saw
    const ingredient = ref<RecipeIngredient>({});
    const { hasSubstitutions, recipeSubstitutions } = useIngredientSubstitutions(() => ingredient.value);

    expect(hasSubstitutions.value).toStrictEqual(false);

    ingredient.value = { substitutions: [{ note: "pork works" }] };

    expect(hasSubstitutions.value).toStrictEqual(true);
    expect(recipeSubstitutions.value[0]?.note).toStrictEqual("pork works");
  });
});

describe("ingredientSubstitutionSummary", () => {
  test("renders each of the three forms a substitution can take", () => {
    const summary = ingredientSubstitutionSummary({
      substitutions: [
        { substituteFoodId: broth.id, substituteFood: broth },
        { note: "water and a bouillon cube" },
        { substituteFoodId: pork.id, substituteFood: pork, note: "works fine" },
      ],
    });

    expect(summary).toStrictEqual("Chicken broth, water and a bouillon cube, Pork (works fine)");
  });

  test("puts what the recipe says ahead of what the food suggests", () => {
    const summary = ingredientSubstitutionSummary({
      food: foodWithSubstitutions(),
      substitutions: [{ substituteFoodId: pork.id, substituteFood: pork }],
    });

    expect(summary).toStrictEqual("Pork, Chicken broth");
  });

  test("is empty when there is nothing to show, which is also the don't-render signal", () => {
    expect(ingredientSubstitutionSummary({})).toStrictEqual("");
    expect(ingredientSubstitutionSummary({ food: { id: "stock-id", name: "Chicken stock" } })).toStrictEqual("");
  });

  test("inflects the substitute foods when the line they replace is plural", () => {
    const ingredient: RecipeIngredient = {
      quantity: 2,
      food: { id: "onion-id", name: "Onion", pluralName: "Onions" },
      substitutions: [{ substituteFoodId: shallot.id, substituteFood: shallot, note: "milder" }],
    };

    const summary = ingredientSubstitutionSummary(ingredient, true);

    expect(summary).toStrictEqual("Shallots (milder)");
  });

  test("skips a substitution carrying neither a food nor a note", () => {
    const summary = ingredientSubstitutionSummary({
      substitutions: [{}, { note: "pork works" }],
    });

    expect(summary).toStrictEqual("pork works");
  });
});
