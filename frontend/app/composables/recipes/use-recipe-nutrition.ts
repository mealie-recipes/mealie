import { standardizedMagnitude } from "./use-unit-conversion";
import type { Nutrition, RecipeIngredient } from "~/lib/api/types/recipe";

export interface NutritionLabelType {
  [key: string]: {
    label: string;
    suffix: string;
    value?: string;
  };
};

export function parseNutritionValue(value: string | null | undefined): number | null {
  if (!value) {
    return null;
  }

  const parsedValue = Number.parseFloat(value);
  return Number.isFinite(parsedValue) ? parsedValue : null;
}

export interface RecipeWeightEstimate {
  /** Estimated total recipe weight in grams, from ingredients whose unit converts to a weight. */
  grams: number;
  /** How many ingredients (with a quantity) contributed to the estimate. */
  matched: number;
  /** How many ingredients had a quantity at all, and so could in principle have contributed. */
  total: number;
}

/**
 * Estimate a recipe's total weight from its ingredients.
 *
 * Mass units (g, kg, oz, lb) convert exactly. Volume units (ml, l, cup, fl oz) are converted
 * assuming water density (1ml = 1g) - a real approximation, since actual ingredient density
 * varies (flour is lighter, honey is heavier). Ingredients with no quantity, no unit, or a unit
 * that doesn't map to a standardized one (e.g. "piece", "pinch", "clove") can't be weighed at all
 * and are left out of the total - so this is always an underestimate when a recipe uses any of
 * those, which `matched`/`total` surface to the caller rather than hiding.
 */
export function estimateRecipeWeightGrams(ingredients: RecipeIngredient[]): RecipeWeightEstimate {
  let grams = 0;
  let matched = 0;
  let total = 0;

  for (const ingredient of ingredients) {
    if (!ingredient.quantity) {
      continue;
    }
    total++;

    const magnitude = standardizedMagnitude(ingredient);
    if (!magnitude) {
      continue;
    }

    // Volume is assumed to be water density (1ml ~= 1g); mass is already in grams.
    grams += magnitude.value;
    matched++;
  }

  return { grams, matched, total };
}

/**
 * Derive "per 100g" nutrition from values entered per serving, using an estimated recipe weight.
 * Returns null per field where it can't be computed (no entered value, or no usable weight).
 */
export function estimateNutritionPer100g(nutrition: Nutrition, weightPerServingGrams: number): Nutrition {
  if (!(weightPerServingGrams > 0)) {
    return { ...nutrition };
  }

  const result = { ...nutrition } as Record<string, string | null | undefined>;
  for (const key of Object.keys(nutrition) as (keyof Nutrition)[]) {
    const parsed = parseNutritionValue(nutrition[key] as string | null | undefined);
    result[key] = parsed === null ? null : ((parsed / weightPerServingGrams) * 100).toFixed(2);
  }

  return result as Nutrition;
}

export function useNutritionLabels() {
  const i18n = useI18n();
  const labels = <NutritionLabelType>{
    calories: {
      label: i18n.t("recipe.calories"),
      suffix: i18n.t("recipe.calories-suffix"),
    },
    carbohydrateContent: {
      label: i18n.t("recipe.carbohydrate-content"),
      suffix: i18n.t("recipe.grams"),
    },
    cholesterolContent: {
      label: i18n.t("recipe.cholesterol-content"),
      suffix: i18n.t("recipe.milligrams"),
    },
    fatContent: {
      label: i18n.t("recipe.fat-content"),
      suffix: i18n.t("recipe.grams"),
    },
    fiberContent: {
      label: i18n.t("recipe.fiber-content"),
      suffix: i18n.t("recipe.grams"),
    },
    proteinContent: {
      label: i18n.t("recipe.protein-content"),
      suffix: i18n.t("recipe.grams"),
    },
    saturatedFatContent: {
      label: i18n.t("recipe.saturated-fat-content"),
      suffix: i18n.t("recipe.grams"),
    },
    sodiumContent: {
      label: i18n.t("recipe.sodium-content"),
      suffix: i18n.t("recipe.milligrams"),
    },
    sugarContent: {
      label: i18n.t("recipe.sugar-content"),
      suffix: i18n.t("recipe.grams"),
    },
    transFatContent: {
      label: i18n.t("recipe.trans-fat-content"),
      suffix: i18n.t("recipe.grams"),
    },
    unsaturatedFatContent: {
      label: i18n.t("recipe.unsaturated-fat-content"),
      suffix: i18n.t("recipe.grams"),
    },
  };

  return { labels };
}
