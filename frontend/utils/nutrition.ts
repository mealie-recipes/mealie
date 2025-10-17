/**
 * Nutrition calculation utilities for meal planning
 *
 * This module provides functions to normalize and aggregate nutritional data
 * from recipes, handling various edge cases like missing data and string-based servings.
 */

import type { Nutrition, Recipe } from "~/lib/api/types/recipe";

export interface Macros {
  calories?: number;
  protein?: number;
  fat?: number;
  carbohydrate?: number;
  carbs?: number; // Alias for carbohydrate
}

/**
 * Converts a value to a number, handling strings and nulls.
 * Tolerant parser that extracts numbers from strings like "4 Portionen".
 */
export function toNum(value: string | number | null | undefined): number {
  if (value === null || value === undefined || value === "") {
    return 0;
  }

  if (typeof value === "number") {
    return value;
  }

  // Extract first number from string (handles "4 Portionen", "2.5 servings", etc.)
  const match = value.toString().match(/[\d.]+/);
  if (match) {
    const num = parseFloat(match[0]);
    return isNaN(num) ? 0 : num;
  }

  return 0;
}

/**
 * Rounds a number to specified decimal places
 */
export function round(value: number, decimals: number = 1): number {
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}

/**
 * Extracts the servings count from a recipe.
 * Checks recipeServings, recipeYieldQuantity, and recipeYield (in that order).
 * Falls back to 1 if no valid value is found.
 */
export function getRecipeServings(recipe: Recipe): number {
  // Priority 1: recipeServings
  if (recipe.recipeServings && recipe.recipeServings > 0) {
    return recipe.recipeServings;
  }

  // Priority 2: recipeYieldQuantity
  if (recipe.recipeYieldQuantity && recipe.recipeYieldQuantity > 0) {
    return recipe.recipeYieldQuantity;
  }

  // Priority 3: recipeYield (may be a string like "4 Portionen")
  if (recipe.recipeYield) {
    const servings = toNum(recipe.recipeYield);
    if (servings > 0) {
      return servings;
    }
  }

  // Default: assume 1 serving
  return 1;
}

/**
 * Normalizes recipe nutrition to per-serving values.
 *
 * IMPORTANT: This function applies a conservative normalization strategy.
 * If recipe.servings > 1, all nutrition values are divided by the serving count,
 * assuming the stored values represent the entire recipe.
 *
 * @param recipe The recipe with nutrition data
 * @returns Nutrition values normalized to 1 serving
 */
export function perOneServing(recipe: Recipe): Required<Macros> {
  const servings = getRecipeServings(recipe);
  const nutrition = recipe.nutrition;

  if (!nutrition) {
    return {
      calories: 0,
      protein: 0,
      fat: 0,
      carbohydrate: 0,
      carbs: 0,
    };
  }

  // Extract raw values
  const calories = toNum(nutrition.calories);
  const protein = toNum(nutrition.proteinContent);
  const fat = toNum(nutrition.fatContent);
  const carbs = toNum(nutrition.carbohydrateContent);

  // Normalize by servings if > 1
  // This is the conservative assumption: stored values are for the whole recipe
  const divisor = servings > 1 ? servings : 1;

  return {
    calories: round(calories / divisor, 0), // Calories as integers
    protein: round(protein / divisor, 1),
    fat: round(fat / divisor, 1),
    carbohydrate: round(carbs / divisor, 1),
    carbs: round(carbs / divisor, 1),
  };
}

/**
 * Scales per-serving nutrition values for a planned serving count.
 *
 * @param perServing Nutrition values for 1 serving (from perOneServing)
 * @param plannedServings Number of servings planned
 * @returns Scaled nutrition values
 */
export function scaleForServings(
  perServing: Required<Macros>,
  plannedServings: number
): Required<Macros> {
  const scale = plannedServings || 1;

  return {
    calories: round(perServing.calories * scale, 0),
    protein: round(perServing.protein * scale, 1),
    fat: round(perServing.fat * scale, 1),
    carbohydrate: round(perServing.carbohydrate * scale, 1),
    carbs: round(perServing.carbs * scale, 1),
  };
}

/**
 * Sums an array of Macros objects.
 *
 * @param items Array of macro values to sum
 * @returns Aggregated totals
 */
export function sumMacros(items: Required<Macros>[]): Required<Macros> {
  const sum = items.reduce(
    (acc, item) => ({
      calories: acc.calories + item.calories,
      protein: acc.protein + item.protein,
      fat: acc.fat + item.fat,
      carbohydrate: acc.carbohydrate + item.carbohydrate,
      carbs: acc.carbs + item.carbs,
    }),
    { calories: 0, protein: 0, fat: 0, carbohydrate: 0, carbs: 0 }
  );

  // Round final sums
  return {
    calories: round(sum.calories, 0),
    protein: round(sum.protein, 1),
    fat: round(sum.fat, 1),
    carbohydrate: round(sum.carbohydrate, 1),
    carbs: round(sum.carbs, 1),
  };
}
