import DOMPurify from "isomorphic-dompurify";
import { useFraction } from "./use-fraction";
import { useLocales } from "../use-locales";
import type { CreateIngredientFood, CreateIngredientUnit, IngredientFood, IngredientUnit, Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

const { frac } = useFraction();

const FRAC_MIN_DENOM = 10;
const DECIMAL_PRECISION = 3;

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

function useRecipeLink(recipe: Recipe | undefined, groupSlug: string | undefined): string | undefined {
  if (!(recipe && recipe.slug && recipe.name && groupSlug)) {
    return undefined;
  }

  return `<a href="/g/${groupSlug}/r/${recipe.slug}" target="_blank">${recipe.name}</a>`;
}

type ParsedIngredientText = {
  quantity?: string;
  unit?: string;
  name?: string;
  note?: string;

  /**
   * If the ingredient is a linked recipe, an HTML link to the referenced recipe, otherwise undefined.
   */
  recipeLink?: string;
};

function shouldUsePluralFood(quantity: number, hasUnit: boolean, pluralFoodHandling: string): boolean {
  if (quantity && quantity <= 1) {
    return false;
  }

  switch (pluralFoodHandling) {
    case "always":
      return true;
    case "without-unit":
      return !(quantity && hasUnit);
    case "never":
      return false;

    default:
      // same as without-unit
      return !(quantity && hasUnit);
  }
}

export function useIngredientTextParser() {
  const { locales, locale } = useLocales();

  function useParsedIngredientText(ingredient: RecipeIngredient, scale = 1, includeFormating = true, groupSlug?: string): ParsedIngredientText {
    const filteredLocales = locales.filter(lc => lc.value === locale.value);
    const pluralFoodHandling = filteredLocales.length ? filteredLocales[0].pluralFoodHandling : "without-unit";

    const { quantity, food, unit, note, referencedRecipe } = ingredient;
    const usePluralUnit = quantity !== undefined && ((quantity || 0) * scale > 1 || (quantity || 0) * scale === 0);
    const usePluralFood = shouldUsePluralFood((quantity || 0) * scale, !!unit, pluralFoodHandling);

    let returnQty = "";

    // casting to number is required as sometimes quantity is a string
    if (quantity && Number(quantity) !== 0) {
      const scaledQuantity = Number((quantity * scale));

      if (unit && !unit.fraction) {
        const minVal = 10 ** -DECIMAL_PRECISION;
        returnQty = scaledQuantity >= minVal
          ? Number(scaledQuantity.toPrecision(DECIMAL_PRECISION)).toString()
          : `< ${minVal}`;
      }
      else {
        const minVal = 1 / FRAC_MIN_DENOM;
        const isUnderMinVal = !(scaledQuantity >= minVal);

        const fraction = !isUnderMinVal ? frac(scaledQuantity, FRAC_MIN_DENOM, true) : [0, 1, FRAC_MIN_DENOM];
        if (fraction[0] !== undefined && fraction[0] > 0) {
          returnQty += fraction[0];
        }

        if (fraction[1] > 0) {
          returnQty += includeFormating
            ? `<sup>${fraction[1]}</sup><span>&frasl;</span><sub>${fraction[2]}</sub>`
            : ` ${fraction[1]}/${fraction[2]}`;
        }

        if (isUnderMinVal) {
          returnQty = `< ${returnQty}`;
        }
      }
    }

    const unitName = useUnitName(unit || undefined, usePluralUnit);
    const ingName = referencedRecipe ? referencedRecipe.name || "" : useFoodName(food || undefined, usePluralFood);

    return {
      quantity: returnQty ? sanitizeIngredientHTML(returnQty) : undefined,
      unit: unitName && quantity ? sanitizeIngredientHTML(unitName) : undefined,
      name: ingName ? sanitizeIngredientHTML(ingName) : undefined,
      note: note ? sanitizeIngredientHTML(note) : undefined,
      recipeLink: useRecipeLink(referencedRecipe || undefined, groupSlug),
    };
  };

  function parseIngredientText(ingredient: RecipeIngredient, scale = 1, includeFormating = true): string {
    const { quantity, unit, name, note } = useParsedIngredientText(ingredient, scale, includeFormating);

    const text = `${quantity || ""} ${unit || ""} ${name || ""} ${note || ""}`.replace(/ {2,}/g, " ").trim();
    return sanitizeIngredientHTML(text);
  };

  return {
    useParsedIngredientText,
    parseIngredientText,
  };
}
