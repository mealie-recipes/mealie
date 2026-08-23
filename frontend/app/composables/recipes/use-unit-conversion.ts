import type { CreateIngredientUnit, RecipeIngredient, RecipeStep } from "~/lib/api/types/recipe";
import type { StandardizedUnitType } from "~/lib/api/types/non-generated";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";

/**
 * Display-time unit conversion.
 *
 * The backend stores what the recipe author wrote and additionally standardizes every
 * unit into a `standardQuantity` x `standardUnit` pair (see the `ingredient_units` table
 * and `RepositoryUnit._add_standardized_unit`). That is everything needed to re-express a
 * quantity in another unit of the same dimension, so conversion happens here rather than
 * behind an API call: no round trip, works in cook mode and print, and — because the
 * caller passes the recipe scale — the display unit can be picked from the *scaled*
 * magnitude, so 10x a 100 g ingredient reads "1 kg" instead of "1000 g".
 *
 * Conversion never crosses dimensions. Cups to grams needs a density per food, which
 * Mealie does not store; those ingredients are passed through untouched.
 */

type Dimension = "mass" | "volume";

/** Amount of the base unit (gram for mass, milliliter for volume) in one canonical unit. */
const CANONICAL_UNITS: Record<StandardizedUnitType, { dimension: Dimension; base: number }> = {
  gram: { dimension: "mass", base: 1 },
  kilogram: { dimension: "mass", base: 1000 },
  ounce: { dimension: "mass", base: 28.349523125 },
  pound: { dimension: "mass", base: 453.59237 },
  milliliter: { dimension: "volume", base: 1 },
  liter: { dimension: "volume", base: 1000 },
  fluid_ounce: { dimension: "volume", base: 29.5735295625 },
  cup: { dimension: "volume", base: 236.5882365 },
};

/**
 * Units the picker can choose from. `key` doubles as the i18n lookup
 * (`unit-names.<key>.name` / `.plural` / `.abbreviation` / `.plural-abbreviation`).
 *
 * `fraction` follows kitchen convention rather than the source unit: metric amounts are
 * written as decimals ("237 ml"), customary ones as fractions ("3/4 cup"). Without this the
 * ingredient parser would render a converted 236.59 ml as "236 5/8".
 */
export type DisplayUnitKey
  = | "milligram" | "gram" | "kilogram"
    | "milliliter" | "liter"
    | "teaspoon" | "tablespoon" | "cup"
    | "imperial-pint"
    | "ounce" | "pound";

const DISPLAY_UNITS: Record<DisplayUnitKey, { base: number; fraction: boolean }> = {
  "milligram": { base: 0.001, fraction: false },
  "gram": { base: 1, fraction: false },
  "kilogram": { base: 1000, fraction: false },
  "milliliter": { base: 1, fraction: false },
  "liter": { base: 1000, fraction: false },
  "teaspoon": { base: 4.92892159375, fraction: true },
  "tablespoon": { base: 14.78676478125, fraction: true },
  "cup": { base: 236.5882365, fraction: true },
  "imperial-pint": { base: 568.26125, fraction: true },
  "ounce": { base: 28.349523125, fraction: true },
  "pound": { base: 453.59237, fraction: true },
};

const QUARTER_CUP = DISPLAY_UNITS.cup.base / 4;

/**
 * Pick the unit a magnitude should be displayed in.
 *
 * `magnitude` is in the dimension's base unit (g or ml) and already scaled, so the
 * thresholds react to what the reader actually sees.
 */
export function pickDisplayUnit(
  dimension: Dimension,
  magnitude: number,
  system: Exclude<UnitSystem, "original">,
): DisplayUnitKey {
  const value = Math.abs(magnitude);

  if (dimension === "mass") {
    if (system === "metric") {
      if (value >= 1000) return "kilogram";
      if (value > 0 && value < 1) return "milligram";
      return "gram";
    }
    // The avoirdupois ounce and pound are identical in UK imperial and US customary.
    return value >= DISPLAY_UNITS.pound.base ? "pound" : "ounce";
  }

  if (system === "metric") {
    return value >= 1000 ? "liter" : "milliliter";
  }

  if (system === "imperial") {
    // Pint's `imperial_cup` is 284 ml, but UK and AU recipes overwhelmingly mean 250 ml by
    // "a cup", and there is no agreed imperial teaspoon or tablespoon either. Rendering
    // everything below an imperial pint in ml matches how UK recipes are actually written.
    return value >= DISPLAY_UNITS["imperial-pint"].base ? "imperial-pint" : "milliliter";
  }

  // US customary. Cups carry the whole upper range because that is how US recipes read
  // ("8 1/2 cups", not "4 pints"); below a quarter cup the fractions get unwieldy and
  // tbsp/tsp take over.
  if (value >= QUARTER_CUP) return "cup";
  if (value >= DISPLAY_UNITS.tablespoon.base) return "tablespoon";
  return "teaspoon";
}

type CanonicalAmount = { dimension: Dimension; base: number };

/** The ingredient's authored quantity expressed in the dimension's base unit, if convertible. */
function canonicalAmount(ingredient: RecipeIngredient): CanonicalAmount | null {
  const unit = ingredient.unit;
  if (!unit?.standardUnit || !unit.standardQuantity) {
    return null;
  }

  // standardUnit is a free-form string on the wire: an admin can type anything into the
  // unit editor, so the lookup has to be able to miss.
  const lookup: Record<string, { dimension: Dimension; base: number } | undefined> = CANONICAL_UNITS;
  const canonical = lookup[unit.standardUnit];
  if (!canonical) {
    return null;
  }

  const quantity = ingredient.quantity || 0;
  if (!quantity) {
    return null;
  }

  return {
    dimension: canonical.dimension,
    base: quantity * unit.standardQuantity * canonical.base,
  };
}

export type UnitNameResolver = (key: DisplayUnitKey) => {
  name: string;
  pluralName: string;
  abbreviation: string;
  pluralAbbreviation: string;
};

/**
 * Re-express an ingredient in `system`.
 *
 * The returned quantity is *unscaled* — the display unit is chosen for `quantity * scale`,
 * but the value itself is the plain conversion, so the ingredient can still be handed to
 * `useParsedIngredientText(ingredient, scale)` unchanged. Ingredients that cannot be
 * converted are returned as-is (same object identity), never guessed at.
 */
export function convertIngredient(
  ingredient: RecipeIngredient,
  system: UnitSystem,
  scale: number,
  resolveName: UnitNameResolver,
): RecipeIngredient {
  if (system === "original") {
    return ingredient;
  }

  const canonical = canonicalAmount(ingredient);
  if (!canonical) {
    return ingredient;
  }

  const key = pickDisplayUnit(canonical.dimension, canonical.base * scale, system);
  const target = DISPLAY_UNITS[key];
  const names = resolveName(key);

  const unit: CreateIngredientUnit = {
    ...names,
    description: "",
    fraction: target.fraction,
    // Converted amounts read better abbreviated ("237 ml", not "237 milliliters"),
    // regardless of how the authored unit was configured.
    useAbbreviation: true,
  };

  return {
    ...ingredient,
    quantity: canonical.base / target.base,
    unit,
  };
}

/**
 * Match a temperature: a number or a range, then the unit, written any of the ways recipes
 * write it — `350°F`, `350 F`, `350F`, `350 degrees F`, `350 degrees Fahrenheit`, `350 deg C`.
 *
 * A bare letter must be uppercase; only a degree sign or the word "degrees" licenses a
 * lowercase one. Without that guard "1/2 c sugar" and "2 c water" read as 2 degrees Celsius,
 * because "c" is the seeded abbreviation for cup. The trailing `(?![A-Za-z])` keeps
 * "vitamin C" and "350Free" out, with an exception for the spelled-out unit names.
 *
 * A bare "425 degrees" with no unit at all is deliberately left alone: US recipes mean
 * Fahrenheit by it and European ones Celsius, and there is nothing in the text to tell them
 * apart. Guessing would silently corrupt half of them.
 */
// No `i` flag: case-insensitivity is spelled out only where it is safe. A blanket flag would
// make the bare-letter branch match "2 c water" again.
const TEMPERATURE_PATTERN
  = /(\d+(?:\.\d+)?)(?:\s*[-–—]\s*(\d+(?:\.\d+)?))?(?:\s*°\s*([FCfc])(?![A-Za-z])|\s*(?:°\s*)?(?:[Dd]egrees?|[Dd]eg\.?)\s*(?:([Ff]ahrenheit|[Cc]elsius|[Cc]entigrade)\b|([FCfc])(?![A-Za-z]))|\s*([FC])(?![A-Za-z]))/;
const TEMPERATURE_RE = new RegExp(TEMPERATURE_PATTERN, "g");

/** Whether instruction text contains anything the temperature rewriter would touch. */
export function hasTemperature(text: string | null | undefined): boolean {
  return !!text && TEMPERATURE_PATTERN.test(text);
}

function convertTemperatureValue(text: string, from: "F" | "C", to: "F" | "C"): string {
  const value = Number(text);
  const converted = from === to
    ? value
    : from === "F"
      ? (value - 32) * 5 / 9
      : value * 9 / 5 + 32;

  // An integer input stays an integer; nobody writes "176.7°C" for a 350°F oven.
  return text.includes(".") ? `${Number(converted.toFixed(1))}` : `${Math.round(converted)}`;
}

/**
 * Resolve which temperature unit to render, given both preferences.
 * Returns null when instruction text should be left alone.
 */
export function resolveTemperatureTarget(
  system: UnitSystem,
  preference: TemperatureUnit,
): "F" | "C" | null {
  if (preference === "celsius") return "C";
  if (preference === "fahrenheit") return "F";
  if (system === "original") return null;
  return system === "us" ? "F" : "C";
}

/** Rewrite temperatures in instruction text. Returns the input unchanged when there is nothing to do. */
export function convertTemperatures(text: string | null | undefined, target: "F" | "C" | null): string {
  if (!text || !target) {
    return text || "";
  }

  return text.replace(
    TEMPERATURE_RE,
    (
      match,
      lo: string,
      hi: string | undefined,
      degreeSignUnit?: string,
      spelledOutUnit?: string,
      degreeWordUnit?: string,
      bareUnit?: string,
    ) => {
      // Whichever branch matched, the unit is decided by its first letter.
      const raw = degreeSignUnit ?? spelledOutUnit ?? degreeWordUnit ?? bareUnit ?? "";
      const source = raw.charAt(0).toUpperCase() === "F" ? "F" : "C";
      if (source === target) {
        return match;
      }

      const low = convertTemperatureValue(lo, source, target);
      if (hi !== undefined) {
        return `${low}-${convertTemperatureValue(hi, source, target)}°${target}`;
      }
      return `${low}°${target}`;
    },
  );
}

/**
 * Bound to the app's translations. The pure functions above take the resolver as an
 * argument so they can be tested without an i18n instance.
 */
export function useUnitConversion() {
  const i18n = useI18n();

  const resolveName: UnitNameResolver = key => ({
    name: i18n.t(`unit-names.${key}.name`),
    pluralName: i18n.t(`unit-names.${key}.plural`),
    abbreviation: i18n.t(`unit-names.${key}.abbreviation`),
    pluralAbbreviation: i18n.t(`unit-names.${key}.plural-abbreviation`),
  });

  function convertIngredients(ingredients: RecipeIngredient[], system: UnitSystem, scale: number) {
    if (system === "original") {
      return ingredients;
    }
    return ingredients.map(ingredient => convertIngredient(ingredient, system, scale, resolveName));
  }

  function convertInstructions(steps: RecipeStep[], system: UnitSystem, preference: TemperatureUnit) {
    const target = resolveTemperatureTarget(system, preference);
    if (!target) {
      return steps;
    }
    return steps.map((step) => {
      if (!step.text) {
        return step;
      }
      const text = convertTemperatures(step.text, target);
      return text === step.text ? step : { ...step, text };
    });
  }

  return { convertIngredients, convertInstructions, resolveName };
}
