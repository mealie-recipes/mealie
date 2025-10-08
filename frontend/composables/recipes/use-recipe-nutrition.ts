import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useUserApi } from "~/composables/api/api-client";
import type { NutritionUnitsResponse } from "~/lib/api/types/recipe";


export interface NutritionLabelType {
  [key: string]: {
    label: string;
    suffix: string;
    value?: string;
  };
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

/**
 * Composable to fetch nutrition units from backend
 */
export function useNutritionUnits() {
  const api = useUserApi(); // correct export
  const units = ref<string[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchUnits = async () => {
    loading.value = true;
    error.value = null;

    try {
      const res = await api.nutrition.getUnits(); // calls /api/recipes/nutrition/units
      // depending on your ApiRequestInstance type, res may have `.data`
      units.value = (res as NutritionUnitsResponse).units ?? [];
    } catch (e: any) {
      console.error("Failed to fetch nutrition units", e);
      error.value = e?.message || "Failed to load units";
    } finally {
      loading.value = false;
    }
  };

  return { units, loading, error, fetchUnits };
}
