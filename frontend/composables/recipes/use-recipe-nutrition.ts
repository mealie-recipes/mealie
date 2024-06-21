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
    sodiumContent: {
      label: i18n.tc("recipe.sodium-content"),
      suffix: i18n.tc("recipe.milligrams"),
    },
    sugarContent: {
      label: i18n.tc("recipe.sugar-content"),
      suffix: i18n.tc("recipe.grams"),
    },
    carbohydrateContent: {
      label: i18n.tc("recipe.carbohydrate-content"),
      suffix: i18n.tc("recipe.grams"),
    },
  };

  return { labels }
}
