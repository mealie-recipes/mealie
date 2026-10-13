const DURATION_UNITS = [
  ["day", 86400],
  ["hour", 3600],
  ["minute", 60],
  ["second", 1],
] as const;

/** A duration in seconds as localized text, e.g. 5400 -> "1 hour 30 minutes" */
export function formatDuration(seconds: number, locale: string, unitDisplay: "long" | "short" = "long"): string {
  let remaining = Math.round(seconds);
  const parts: string[] = [];

  for (const [unit, size] of DURATION_UNITS) {
    const amount = Math.floor(remaining / size);
    remaining -= amount * size;
    if (amount > 0) {
      parts.push(new Intl.NumberFormat(locale, { style: "unit", unit, unitDisplay }).format(amount));
    }
  }

  return new Intl.ListFormat(locale, { type: "unit", style: "narrow" }).format(parts);
}

interface RecipeTimes {
  totalTimeSeconds?: number | null;
  prepTimeSeconds?: number | null;
  performTimeSeconds?: number | null;
  totalTime?: string | null;
}

/**
 * How long a recipe takes, in the compact form used on cards, e.g. "35 min" or "1 hr 10 min".
 * Falls back to prep plus cook time, then to the recipe's free text, when there is no total.
 */
export function recipeShortTime(recipe: RecipeTimes, locale: string): string {
  const seconds = recipe.totalTimeSeconds || ((recipe.prepTimeSeconds || 0) + (recipe.performTimeSeconds || 0));
  if (seconds) {
    return formatDuration(seconds, locale, "short");
  }
  return recipe.totalTime?.trim() || "";
}

/** The locale's short name for a unit, e.g. "hr" or "min", from the browser rather than our translations */
export function durationUnitLabel(unit: "hour" | "minute", locale: string): string {
  const parts = new Intl.NumberFormat(locale, { style: "unit", unit, unitDisplay: "short" }).formatToParts(2);
  return parts.find(part => part.type === "unit")?.value ?? unit;
}

/** The structured time followed by the recipe's free text, e.g. "3 hours plus overnight", like yield */
export function recipeTimeDisplay(
  seconds: number | null | undefined,
  text: string | null | undefined,
  locale: string,
): string {
  const duration = seconds ? formatDuration(seconds, locale) : "";
  return [duration, text?.trim()].filter(Boolean).join(" ");
}

export function useRecipeTime() {
  const i18n = useI18n();

  return {
    durationUnitLabel: (unit: "hour" | "minute") => durationUnitLabel(unit, i18n.locale.value),
    recipeTimeDisplay: (seconds: number | null | undefined, text: string | null | undefined) =>
      recipeTimeDisplay(seconds, text, i18n.locale.value),
    recipeShortTime: (recipe: RecipeTimes) => recipeShortTime(recipe, i18n.locale.value),
  };
}
