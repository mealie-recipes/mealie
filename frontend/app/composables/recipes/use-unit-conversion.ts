import { CUSTOMARY_SYSTEMS, STANDARDIZED_UNITS, UNIT_SYSTEMS, type StandardizedUnit, type UnitRung, type UnitSystem } from "./unit-systems";
import type { CreateIngredientUnit, RecipeIngredient } from "~/lib/api/types/recipe";

interface ConvertibleIngredient {
  quantity: number;
  standardQuantity: number;
  unit: CreateIngredientUnit;
  standard: StandardizedUnit;
}

/**
 * Resolve the values needed to convert an ingredient, or null if it can't be converted.
 *
 * An ingredient is only convertible if its unit was matched to a standardized unit when it was
 * created. standardUnit is a free-form string on the wire, so it's checked against the table
 * rather than trusted. Volume never becomes weight — that needs a density per food, which we
 * don't store — so anything unrecognized is left alone rather than guessed at.
 */
function resolveConvertible(ingredient: RecipeIngredient): ConvertibleIngredient | null {
  const { quantity, unit } = ingredient;
  if (!quantity || !unit?.standardUnit || !unit.standardQuantity) {
    return null;
  }

  const standard = STANDARDIZED_UNITS[unit.standardUnit];
  if (!standard) {
    return null;
  }

  return { quantity, standardQuantity: unit.standardQuantity, unit, standard };
}

export function canConvertIngredient(ingredient: RecipeIngredient): boolean {
  return resolveConvertible(ingredient) !== null;
}

/**
 * Pick the rung the magnitude falls on. Rungs are ordered smallest first, and each takes over
 * once the magnitude reaches its takeover multiple, so the last one that fits wins.
 */
function pickRung(rungs: UnitRung[], magnitude: number): UnitRung {
  let chosen = rungs[0];
  for (const rung of rungs) {
    if (magnitude >= rung.base * rung.takeover) {
      chosen = rung;
    }
  }

  return chosen;
}

export function useUnitConversion() {
  const { t, te } = useI18n();

  /**
   * Names come from the ingredient unit seed data, which app/lang/locales/*.ts merge into the
   * messages under `unit-names`. That data is already translated into every locale Mealie
   * ships, so nothing here is authored per-locale.
   */
  function unitFromRung(rung: UnitRung, source: CreateIngredientUnit): CreateIngredientUnit {
    const key = `unit-names.${rung.seedKey}`;
    const abbreviation = t(`${key}.abbreviation`);

    return {
      name: t(`${key}.name`),
      pluralName: t(`${key}.plural_name`),
      abbreviation,
      // Most seeded units have no distinct plural abbreviation, and a missing key would render
      // as the key itself rather than falling back to the singular
      pluralAbbreviation: te(`${key}.plural_abbreviation`) ? t(`${key}.plural_abbreviation`) : abbreviation,
      fraction: rung.fraction,
      // Only the unit changes; the reader keeps whatever display style the recipe's own unit used
      useAbbreviation: source.useAbbreviation,
    };
  }

  /**
   * Restate an ingredient in the given unit system. Display only — nothing is written back.
   *
   * An ingredient already measured in the reader's own system is returned untouched, so
   * choosing a system only ever rewrites units that are foreign to it.
   *
   * Where conversion does happen, the display unit is chosen from the *scaled* magnitude while
   * the quantity returned stays unscaled, so callers keep applying scale themselves and
   * existing call sites are unaffected. 4oz of something at 10x comes back as 1.13 kilogram
   * rather than 1134 grams.
   *
   * Ingredients that can't be converted are returned unchanged, with the same object identity.
   */
  function convertIngredient(ingredient: RecipeIngredient, system: UnitSystem, scale = 1): RecipeIngredient {
    const convertible = resolveConvertible(ingredient);
    if (!convertible) {
      return ingredient;
    }

    const { quantity, standardQuantity, unit, standard } = convertible;

    // Already written in the system the reader asked for, so leave it exactly as authored
    // rather than restating "1 pint" as "2 cups". Only genuinely foreign units get rewritten.
    if (standard.customary === CUSTOMARY_SYSTEMS.includes(system)) {
      return ingredient;
    }

    const magnitude = quantity * standardQuantity * standard.base;
    const rung = pickRung(UNIT_SYSTEMS[system][standard.dimension], magnitude * scale);

    return {
      ...ingredient,
      quantity: magnitude / rung.base,
      unit: unitFromRung(rung, unit),
    };
  }

  return { convertIngredient };
}
