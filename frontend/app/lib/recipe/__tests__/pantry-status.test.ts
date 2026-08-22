import { describe, expect, test } from "vitest";
import type { IngredientFood, Recipe, RecipeIngredient } from "~/lib/api/types/recipe";
import { getRecipePantryStatus } from "~/lib/recipe/pantry-status";

const householdSlug = "home";

function food(id: string, name: string, onHand = false): IngredientFood {
  return {
    id,
    name,
    householdsWithIngredientFood: onHand ? [householdSlug] : [],
  } as IngredientFood;
}

function recipe(id: string, ingredients: RecipeIngredient[]): Recipe {
  return { id, slug: id, name: id, recipeIngredient: ingredients } as Recipe;
}

describe("getRecipePantryStatus", () => {
  test("separates on-hand and missing structured foods and deduplicates them", () => {
    const flour = food("flour", "Flour", true);
    const salt = food("salt", "Salt");
    const status = getRecipePantryStatus(
      recipe("bread", [
        { food: flour },
        { food: salt },
        { food: salt },
        { note: "a splash of water" },
      ]),
      householdSlug,
    );

    expect(status.structuredFoods.map(item => item.name)).toEqual(["Flour", "Salt"]);
    expect(status.onHandFoods.map(item => item.name)).toEqual(["Flour"]);
    expect(status.missingFoods.map(item => item.name)).toEqual(["Salt"]);
    expect(status.unlinkedIngredientCount).toBe(1);
  });

  test("includes structured foods from referenced recipes", () => {
    const sauce = recipe("sauce", [{ food: food("tomato", "Tomato") }]);
    const status = getRecipePantryStatus(
      recipe("pasta", [{ referencedRecipe: sauce }]),
      householdSlug,
    );

    expect(status.missingFoods.map(item => item.name)).toEqual(["Tomato"]);
  });
});
