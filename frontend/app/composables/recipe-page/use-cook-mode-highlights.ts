import type { RecipeIngredient } from "~/lib/api/types/recipe";

/**
 * Cook mode tints the ingredients a step mentions ("Add the *onion* and *pepper*") so they can be
 * picked out from across the room. These helpers work on the step's markdown source, before it is
 * rendered, and leave links, inline code and HTML untouched.
 */

export const HIGHLIGHT_CLASS = "cook-hl";

// common words that would otherwise light up for unparsed ingredients ("large eggs" vs "large pan")
const IGNORED_WORDS = new Set([
  "and", "the", "for", "with", "without", "into", "onto", "from", "until", "each", "more", "some",
  "large", "small", "medium", "fresh", "chopped", "diced", "minced", "sliced", "ground", "whole",
  "cup", "cups", "tbsp", "tsp", "taste", "about", "over", "heat", "pan", "pot", "add", "stir",
]);

const PROTECTED = /(`[^`]*`|!?\[[^\]]*\]\([^)]*\)|<[^>]+>|https?:\/\/\S+)/g;

function escapeRegExp(text: string) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function words(text: string): string[] {
  return text
    .toLowerCase()
    .split(/[^\p{L}\p{N}'-]+/u)
    .map(word => word.replace(/^['-]+|['-]+$/g, ""))
    .filter(word => word.length > 2 && !/\d/.test(word) && !IGNORED_WORDS.has(word));
}

/**
 * The words to highlight in a step for the ingredients it uses: each food's name, or for an
 * ingredient that was never parsed into a food, the words its text shares with the step.
 */
export function ingredientHighlightTerms(ingredients: RecipeIngredient[], stepText: string): string[] {
  const stepWords = new Set(words(stepText));
  const terms = new Set<string>();

  for (const ingredient of ingredients) {
    const food = ingredient.food;
    if (food?.name) {
      for (const name of [food.name, food.pluralName]) {
        if (!name) {
          continue;
        }
        terms.add(name);
        // the step usually names just the noun: "yellow onion" is "the onion" by then
        const last = words(name).at(-1);
        if (last) {
          terms.add(last);
        }
      }
      continue;
    }

    const text = [ingredient.note, ingredient.originalText, ingredient.display].filter(Boolean).join(" ");
    for (const word of words(text)) {
      if (stepWords.has(word)) {
        terms.add(word);
      }
    }
  }

  return [...terms].filter(term => term.trim().length > 1);
}

/** Wraps each whole-word mention of a term in a highlight span, plural "s"/"es" included */
export function highlightTerms(source: string, terms: string[]): string {
  if (!source || !terms.length) {
    return source || "";
  }

  // longest first, so "red pepper" wins over "pepper"
  const alternatives = [...terms]
    .sort((a, b) => b.length - a.length)
    .map(term => escapeRegExp(term.trim()))
    .join("|");
  const pattern = new RegExp(`(?<![\\p{L}\\p{N}])(?:${alternatives})(?:e?s)?(?![\\p{L}\\p{N}])`, "giu");

  return source
    .split(PROTECTED)
    .map((segment, index) => {
      // split() with a capture group puts the protected pieces at odd indexes
      if (index % 2 === 1) {
        return segment;
      }
      return segment.replace(pattern, match => `<span class="${HIGHLIGHT_CLASS}">${match}</span>`);
    })
    .join("");
}
