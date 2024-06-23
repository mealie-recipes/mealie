import { RecipeIngredient } from "~/lib/api/types/recipe";
import { parseIngredientText } from "~/composables/recipes";


function normalize(word: string): string {
    let normalizing = word;
    normalizing = removeTrailingPunctuation(normalizing);
    normalizing = removeStartingPunctuation(normalizing);
    return normalizing;
}

function removeTrailingPunctuation(word: string): string {
    const punctuationAtEnding = /\p{P}+$/u;
    return word.replace(punctuationAtEnding, "");
}

function removeStartingPunctuation(word: string): string {
    const punctuationAtBeginning = /^\p{P}+/u;
    return word.replace(punctuationAtBeginning, "");
}

function ingredientMatchesWord(ingredient: RecipeIngredient, word: string, recipeIngredientAmountsDisabled: boolean) {
    const searchText = parseIngredientText(ingredient, recipeIngredientAmountsDisabled);
    return searchText.toLowerCase().includes(word.toLowerCase());
}

function isBlackListedWord(word: string) {
    // Ignore matching blacklisted words when auto-linking - This is kind of a cludgey implementation. We're blacklisting common words but
    // other common phrases trigger false positives and I'm not sure how else to approach this. In the future I maybe look at looking directly
    // at the food variable and seeing if the food is in the instructions, but I still need to support those who don't want to provide the value
    // and only use the "notes" feature.
    const blackListedText: string[] = [
        "and",
        "the",
        "for",
        "with",
        "without"
    ];
    const blackListedRegexMatch = /\d/gm; // Match Any Number
    return blackListedText.includes(word) || word.match(blackListedRegexMatch);
}

export function useExtractIngredientReferences(recipeIngredients: RecipeIngredient[], activeRefs: string[], text: string, recipeIngredientAmountsDisabled: boolean): Set<string> {
    const availableIngredients = recipeIngredients
        .filter((ingredient) => ingredient.referenceId !== undefined)
        .filter((ingredient) => !activeRefs.includes(ingredient.referenceId as string));

    const allMatchedIngredientIds: string[] = text
        .toLowerCase()
        .split(/\s/)
        .map(normalize)
        .filter((word) => word.length > 2)
        .filter((word) => !isBlackListedWord(word))
        .flatMap((word) => availableIngredients.filter((ingredient) => ingredientMatchesWord(ingredient, word, recipeIngredientAmountsDisabled)))
        .map((ingredient) => ingredient.referenceId as string);
    //  deduplicate

    return new Set<string>(allMatchedIngredientIds)

}
