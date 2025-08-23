import DOMPurify from "isomorphic-dompurify";
import { useFraction } from "./use-fraction";
import type { CreateIngredientFood, CreateIngredientUnit, IngredientFood, IngredientUnit, RecipeIngredient } from "~/lib/api/types/recipe";
import type { GroupPreferencesPluralHandling } from "~/lib/api/types/group";

const { frac } = useFraction();

export function sanitizeIngredientHTML(rawHtml: string) {
  return DOMPurify.sanitize(rawHtml, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: ["b", "q", "i", "strong", "sup"],
  });
}

function useFoodName(food: CreateIngredientFood | IngredientFood | undefined, usePlural: boolean) {
  if (!food) {
    return "";
  }

  return (usePlural ? food.pluralName || food.name : food.name) || "";
}

function useUnitName(unit: CreateIngredientUnit | IngredientUnit | undefined, usePlural: boolean) {
  if (!unit) {
    return "";
  }

  let returnVal = "";
  if (unit.useAbbreviation) {
    returnVal = (usePlural ? unit.pluralAbbreviation || unit.abbreviation : unit.abbreviation) || "";
  }

  if (!returnVal) {
    returnVal = (usePlural ? unit.pluralName || unit.name : unit.name) || "";
  }

  return returnVal;
}

export function useParsedIngredientText(
  ingredient: RecipeIngredient,
  scale = 1,
  includeFormating = true,
  pluralHandling = "pluralize_food_without_unit" as GroupPreferencesPluralHandling,
) {
  const { quantity, food, unit, note } = ingredient;

  // casting to number is required as sometimes quantity is a string
  const scaledQuantity = (Number(quantity || 0)) * scale;
  const usePluralUnit = (scaledQuantity && scaledQuantity > 1) || false;

  let usePluralFood = false;
  if (scaledQuantity && scaledQuantity <= 1) {
    usePluralFood = false;
  } else {
    switch (pluralHandling) {
      case "disable":
        usePluralFood = false;
        break;
      case "pluralize_food_without_unit":
        // if quantity is zero then unit is not shown even if it's set
        usePluralFood = !(scaledQuantity && unit);
        break;
      case "always_pluralize":
        usePluralFood = true;
        break;
      default:
        usePluralFood = false;
        break;
    }
  }

  let returnQty = "";

  if (scaledQuantity) {
    if (unit && !unit.fraction) {
      returnQty = Number(scaledQuantity.toPrecision(3)).toString();
    }
    else {
      const fraction = frac(scaledQuantity, 10, true);
      if (fraction[0] !== undefined && fraction[0] > 0) {
        returnQty += fraction[0];
      }

      if (fraction[1] > 0) {
        returnQty += includeFormating
          ? `<sup>${fraction[1]}</sup><span>&frasl;</span><sub>${fraction[2]}</sub>`
          : ` ${fraction[1]}/${fraction[2]}`;
      }
    }
  }

  const unitName = useUnitName(unit || undefined, usePluralUnit);
  const foodName = useFoodName(food || undefined, usePluralFood);

  return {
    quantity: returnQty ? sanitizeIngredientHTML(returnQty) : undefined,
    unit: unitName && quantity ? sanitizeIngredientHTML(unitName) : undefined,
    name: foodName ? sanitizeIngredientHTML(foodName) : undefined,
    note: note ? sanitizeIngredientHTML(note) : undefined,
  };
}

export function parseIngredientText(
  ingredient: RecipeIngredient, scale = 1,
  includeFormating = true,
  pluralHandling = "pluralize_food_without_unit" as GroupPreferencesPluralHandling,
): string {
  const { quantity, unit, name, note } = useParsedIngredientText(ingredient, scale, includeFormating, pluralHandling);

  const text = `${quantity || ""} ${unit || ""} ${name || ""} ${note || ""}`.replace(/ {2,}/g, " ").trim();
  return sanitizeIngredientHTML(text);
}
