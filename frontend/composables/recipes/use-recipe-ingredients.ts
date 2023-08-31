import DOMPurify from "isomorphic-dompurify";
import { useFraction } from "./use-fraction";
import { RecipeIngredient } from "~/lib/api/types/recipe";
const { frac } = useFraction();

function sanitizeIngredientHTML(rawHtml: string) {
  return DOMPurify.sanitize(rawHtml, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: ["b", "q", "i", "strong", "sup"],
  });
}

export function useParsedIngredientText(ingredient: RecipeIngredient, disableAmount: boolean, scale = 1, includeFormating = true) {
  if (disableAmount) {
    return {
      name: ingredient.note ? sanitizeIngredientHTML(ingredient.note) : undefined,
      quantity: undefined,
      unit: undefined,
      note: undefined,
    };
  }

  const { quantity, food, unit, note } = ingredient;

  let returnQty = "";

  let unitDisplay = unit?.name;

  // casting to number is required as sometimes quantity is a string
  if (quantity && Number(quantity) !== 0) {
    if (unit?.fraction) {
      const fraction = frac(quantity * scale, 10, true);
      if (fraction[0] !== undefined && fraction[0] > 0) {
        returnQty += fraction[0];
      }

      if (fraction[1] > 0) {
        returnQty += includeFormating ?
          ` <sup>${fraction[1]}</sup>&frasl;<sub>${fraction[2]}</sub>` :
          ` ${fraction[1]}/${fraction[2]}`;
      }
    } else {
      returnQty = (quantity * scale).toString();
    }

    if (unit?.useAbbreviation && unit.abbreviation) {
      unitDisplay = unit.abbreviation;
    }
  }

  return {
    quantity: returnQty ? sanitizeIngredientHTML(returnQty) : undefined,
    unit: unitDisplay ? sanitizeIngredientHTML(unitDisplay) : undefined,
    name: food?.name ? sanitizeIngredientHTML(food.name) : undefined,
    note: note ? sanitizeIngredientHTML(note) : undefined,
  };
}

export function parseIngredientText(ingredient: RecipeIngredient, disableAmount: boolean, scale = 1, includeFormating = true): string {
  const { quantity, unit, name, note } = useParsedIngredientText(ingredient, disableAmount, scale, includeFormating);

  const text = `${quantity || ""} ${unit || ""} ${name || ""} ${note || ""}`.replace(/ {2,}/g, " ").trim();
  return sanitizeIngredientHTML(text);
}
