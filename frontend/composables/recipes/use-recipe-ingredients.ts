import { useFraction } from "./use-fraction";
import { RecipeIngredient } from "~/types/api-types/recipe";

const { frac } = useFraction();

export function parseIngredientText(ingredient: RecipeIngredient, disableAmount: boolean, scale: number = 1): string {
  if (disableAmount) {
    return ingredient.note;
  }

  const { quantity, food, unit, note } = ingredient;

  const validQuantity = quantity !== null && quantity !== undefined && quantity !== 0;

  let returnQty = "";
  if (unit?.fraction) {
    const fraction = frac(quantity * scale, 10, true);
    if (fraction[0] !== undefined && fraction[0] > 0) {
      returnQty += fraction[0];
    }

    if (fraction[1] > 0) {
      returnQty += ` <sup>${fraction[1]}</sup>&frasl;<sub>${fraction[2]}</sub>`;
    }
  } else if (validQuantity) {
    returnQty = (quantity * scale).toString();
  } else {
    returnQty = "";
  }

  return `${returnQty} ${unit?.name || " "}  ${food?.name || " "} ${note}`.replace(/ {2,}/g, " ");
}
