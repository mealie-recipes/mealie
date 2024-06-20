import { getLowestFraction } from "../recipes/use-fraction";
import { formatFraction } from "../recipes/use-recipe-ingredients";

const matchMixedFraction = /(?:\d*\s\d*\d*|0)\/\d*\d*/;
const matchFraction = /(?:\d*\d*|0)\/\d*\d*/;
const matchDecimal = /(\d+.\d+)|(.\d+)/;
const matchInt = /\d+/;



function extractServingsFromMixedFraction(fractionString: string): number | undefined {
    const mixedSplit = fractionString.split(/\s/);
    const wholeNumber = parseInt(mixedSplit[0]);
    const fraction = mixedSplit[1];

    const fractionSplit = fraction.split("/");
    const numerator = parseInt(fractionSplit[0]);
    const denominator = parseInt(fractionSplit[1]);

    if (denominator === 0) {
        return undefined;  // if the denominator is zero, just give up
    }
    else {
        return wholeNumber + (numerator / denominator);
    }
}

function extractServingsFromFraction(fractionString: string): number | undefined {
    const fractionSplit = fractionString.split("/");
    const numerator = parseInt(fractionSplit[0]);
    const denominator = parseInt(fractionSplit[1]);

    if (denominator === 0) {
        return undefined;  // if the denominator is zero, just give up
    }
    else {
        return numerator / denominator;
    }
}

function findMatch(yieldString: string): [matchString: string, servings: number] | null {
    if (!yieldString) {
        return null;
    }

    const mixedFractionMatch = yieldString.match(matchMixedFraction);
    if (mixedFractionMatch?.length) {
        const match = mixedFractionMatch[0];
        const servings = extractServingsFromMixedFraction(match);

        // if the denominator is zero, return no match
        if (servings === undefined) {
            return null;
        } else {
            return [match, servings];
        }
    }

    const fractionMatch = yieldString.match(matchFraction);
    if (fractionMatch?.length) {
        const match = fractionMatch[0]
        const servings = extractServingsFromFraction(match);

        // if the denominator is zero, return no match
        if (servings === undefined) {
            return null;
        } else {
            return [match, servings];
        }
    }

    const decimalMatch = yieldString.match(matchDecimal);
    if (decimalMatch?.length) {
        const match = decimalMatch[0];
        return [match, parseFloat(match)];
    }

    const intMatch = yieldString.match(matchInt);
    if (intMatch?.length) {
        const match = intMatch[0];
        return [match, parseInt(match)];
    }

    return null;
}

function formatServings(servings: number, scale: number, includeFormating: boolean): string {
    const val = servings * scale;
    if (Number.isInteger(val)) {
        return val.toString();
    }

    // convert val into a fraction string
    const fraction = getLowestFraction(val);

    return formatFraction(fraction, includeFormating)
}


export function useExtractRecipeYield(yieldString: string | null, scale: number, includeFormating = true): string {
    if (!yieldString) {
        return "";
    }

    const match = findMatch(yieldString);
    if (!match) {
        return yieldString;
    }

    const [matchString, servings] = match;

    const formattedServings = formatServings(servings, scale, includeFormating);
    if (!formattedServings) {
        return yieldString  // this only happens with very weird or small fractions
    } else {
        return yieldString.replace(matchString, " " + formattedServings + " ").replace(/\s\s+/g, " ").trim();
    }
}
