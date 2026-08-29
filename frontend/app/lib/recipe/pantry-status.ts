import type { IngredientFood, Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

export interface RecipePantryStatus {
  onHandFoods: IngredientFood[];
  neededIngredients: string[];
}

export function getRecipePantryStatus(recipe: Recipe, householdSlug: string): RecipePantryStatus {
  const onHandFoods = new Map<string, IngredientFood>();
  const neededIngredients = new Map<string, string>();
  const activeRecipes = new Set<string>();

  function collectIngredients(ingredients: RecipeIngredient[], recipeKey: string) {
    if (activeRecipes.has(recipeKey)) return;
    activeRecipes.add(recipeKey);

    for (const ingredient of ingredients) {
      if (ingredient.referencedRecipe) {
        const referencedRecipe = ingredient.referencedRecipe;
        collectIngredients(
          referencedRecipe.recipeIngredient || [],
          referencedRecipe.id || referencedRecipe.slug || referencedRecipe.name,
        );
      }
      else if (ingredient.food) {
        const key = ingredient.food.id || ingredient.food.name.trim().toLocaleLowerCase();
        if (ingredient.food.householdsWithIngredientFood?.includes(householdSlug)) {
          onHandFoods.set(key, ingredient.food as IngredientFood);
        }
        else {
          neededIngredients.set(key, ingredient.food.name);
        }
      }
      else if (ingredient.note || ingredient.display || ingredient.originalText) {
        const name = ingredient.note || ingredient.display || ingredient.originalText || "";
        neededIngredients.set(name.trim().toLocaleLowerCase(), name);
      }
    }

    activeRecipes.delete(recipeKey);
  }

  collectIngredients(recipe.recipeIngredient || [], recipe.id || recipe.slug);
  const sortByName = <T extends { name: string }>(left: T, right: T) => left.name.localeCompare(right.name);

  return {
    onHandFoods: Array.from(onHandFoods.values()).sort(sortByName),
    neededIngredients: Array.from(neededIngredients.values()).sort((left, right) => left.localeCompare(right)),
  };
}
