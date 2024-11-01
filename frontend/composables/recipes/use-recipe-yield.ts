import DOMPurify from "isomorphic-dompurify";
import { useFraction } from "~/composables/recipes";

function sanitizeHTML(rawHtml: string) {
  return DOMPurify.sanitize(rawHtml, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: ["b", "q", "i", "strong", "sup", "span"],
  });
}

function formatQuantity(val: number): string {
  if (Number.isInteger(val)) {
    return val.toString();
  }

  const { frac } = useFraction();

  let valString = "";
  const fraction = frac(val, 10, true);

  if (fraction[0] !== undefined && fraction[0] > 0) {
      valString += fraction[0];
  }

  if (fraction[1] > 0) {
      valString += `<sup>${fraction[1]}</sup><span>&frasl;</span><sub>${fraction[2]}</sub>`;
  }

  return valString.trim();
}

export function useRecipeYield(recipeYieldQuantity: number, recipeYield: string, scale = 1) {
  const yieldQuantity = Number(((recipeYieldQuantity || 0) * scale).toFixed(3));
  const yieldString = sanitizeHTML(recipeYield || "");
  const yieldQuantityDisplay = yieldQuantity ? formatQuantity(yieldQuantity) : "";

  const yieldDisplay = yieldQuantityDisplay
    ? `${yieldQuantityDisplay} ${yieldString}`.trim()
    : yieldString;

  return {
    yieldQuantity,
    yieldString,
    yieldDisplay,
  };
}
