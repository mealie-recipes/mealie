import { useContext } from "@nuxtjs/composition-api";


export interface NutritionLabelType {
  [key: string]: {
    label: string;
    suffix: string;
    value?: string;
  };
};


export function useNutritionLabels() {
  const { i18n } = useContext();
  const labels = <NutritionLabelType>{
    calories: {
      label: i18n.tc("recipe.calories"),
      suffix: i18n.tc("recipe.calories-suffix"),
    },
    carbohydrateContent: {
      label: i18n.tc("recipe.carbohydrate-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    cholesterolContent: {
      label: i18n.tc("recipe.cholesterol-content"),
      suffix: i18n.tc("recipe.milligrams"),
    },
    fatContent: {
      label: i18n.tc("recipe.fat-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    fiberContent: {
      label: i18n.tc("recipe.fiber-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    proteinContent: {
      label: i18n.tc("recipe.protein-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    saturatedFatContent: {
      label: i18n.tc("recipe.saturated-fat-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    sodiumContent: {
      label: i18n.tc("recipe.sodium-content"),
      suffix: i18n.tc("recipe.milligrams"),
    },
    sugarContent: {
      label: i18n.tc("recipe.sugar-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    transFatContent: {
      label: i18n.tc("recipe.trans-fat-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    unsaturatedFatContent: {
      label: i18n.tc("recipe.unsaturated-fat-content"),
      suffix: i18n.tc("recipe.grams"),
    },
  };

  return { labels }
}
