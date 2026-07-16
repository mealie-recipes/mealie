export interface NutritionLabelType {
  [key: string]: {
    label: string;
    suffix: string;
    value?: string;
  };
};

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
