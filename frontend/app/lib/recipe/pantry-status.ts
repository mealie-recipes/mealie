import type { IngredientFood, Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

export interface RecipePantryStatus {
  structuredFoods: IngredientFood[];
  onHandFoods: IngredientFood[];
  missingFoods: IngredientFood[];
  unlinkedIngredientCount: number;
}

export function getRecipePantryStatus(recipe: Recipe, householdSlug: string): RecipePantryStatus {
  const foods = new Map<string, IngredientFood>();
  let unlinkedIngredientCount = 0;
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
        foods.set(key, ingredient.food as IngredientFood);
      }
      else if (ingredient.note || ingredient.display || ingredient.originalText) {
        unlinkedIngredientCount++;
      }
    }

    activeRecipes.delete(recipeKey);
  }

  collectIngredients(recipe.recipeIngredient || [], recipe.id || recipe.slug);
  const structuredFoods = Array.from(foods.values()).sort((left, right) => left.name.localeCompare(right.name));
  const onHandFoods = structuredFoods.filter(food => food.householdsWithIngredientFood?.includes(householdSlug));
  const missingFoods = structuredFoods.filter(food => !food.householdsWithIngredientFood?.includes(householdSlug));

  return { structuredFoods, onHandFoods, missingFoods, unlinkedIngredientCount };
}
