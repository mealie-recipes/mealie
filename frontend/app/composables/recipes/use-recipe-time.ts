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

const DURATION_WORD_UNIT_RANK = new Map<string, number>([
  ["day", 0],
  ["days", 0],
  ["hour", 1],
  ["hours", 1],
  ["hr", 1],
  ["hrs", 1],
  ["minute", 2],
  ["minutes", 2],
  ["min", 2],
  ["mins", 2],
  ["second", 3],
  ["seconds", 3],
  ["sec", 3],
  ["secs", 3],
]);

const ISO_DURATION_PATTERN = /^P(?=\d|T\d)(?:\d+(?:\.\d+)?W)?(?:\d+(?:\.\d+)?D)?(?:T(?=\d)(?:\d+(?:\.\d+)?H)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?S)?)?$/;
const BARE_NUMBER_PATTERN = /^\d+(?:\.\d+)?$/;

/**
 * Whether the whole text is a duration, in the shapes the structured-time migration clears from
 * the text column: ISO 8601, a bare number of minutes, or English "<n> hour/minute" words.
 * English is enough here because this only suppresses a duplicate in the UI.
 */
function isBareDuration(text: string): boolean {
  const value = text.trim();
  if (BARE_NUMBER_PATTERN.test(value)) {
    return true;
  }

  if (/^p/i.test(value) && ISO_DURATION_PATTERN.test(value.toUpperCase())) {
    return true;
  }

  const component = /\s*(\d+(?:\.\d+)?)\s*([a-z]+)(?=\s|\d|$)/iy;
  let position = 0;
  let previousRank = -1;
  let components = 0;

  while (position < value.length) {
    component.lastIndex = position;
    const match = component.exec(value);
    if (!match) {
      return false;
    }

    const rank = DURATION_WORD_UNIT_RANK.get(match[2].toLowerCase());
    if (rank === undefined || rank <= previousRank) {
      return false;
    }

    previousRank = rank;
    components += 1;
    position = component.lastIndex;
  }

  return components > 0;
}

/**
 * The structured time followed by the recipe's free text, e.g. "3 hours plus overnight".
 *
 * A text that is entirely a duration is machine data: the structured seconds already carry it, and
 * appending it again renders "20 minutes PT20M". Only text with extra words is a human annotation
 * and is appended verbatim. When seconds are absent the text is the only value, so it is kept.
 */
export function recipeTimeDisplay(
  seconds: number | null | undefined,
  text: string | null | undefined,
  locale: string,
): string {
  const duration = seconds ? formatDuration(seconds, locale) : "";
  const textValue = text?.trim() ?? "";
  const parts = duration ? [duration] : [];

  if (textValue && !(seconds && isBareDuration(textValue))) {
    parts.push(textValue);
  }

  return parts.join(" ");
}

export function useRecipeTime() {
  const i18n = useI18n();

  return {
    durationUnitLabel: (unit: "hour" | "minute") => durationUnitLabel(unit, i18n.locale.value),
    recipeTimeDisplay: (seconds: number | null | undefined, text: string | null | undefined) =>
      recipeTimeDisplay(seconds, text, i18n.locale.value),
  };
}
