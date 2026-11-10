const DURATION_UNITS = [
  ["day", 86400],
  ["hour", 3600],
  ["minute", 60],
  ["second", 1],
] as const;

/** A duration in seconds as localized text, e.g. 5400 -> "1 hour 30 minutes" */
export function formatDuration(seconds: number, locale: string): string {
  let remaining = Math.round(seconds);
  const parts: string[] = [];

  for (const [unit, size] of DURATION_UNITS) {
    const amount = Math.floor(remaining / size);
    remaining -= amount * size;
    if (amount > 0) {
      parts.push(new Intl.NumberFormat(locale, { style: "unit", unit, unitDisplay: "long" }).format(amount));
    }
  }

  return new Intl.ListFormat(locale, { type: "unit", style: "narrow" }).format(parts);
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
  };
}
