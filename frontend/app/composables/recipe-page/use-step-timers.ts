/**
 * Finds the durations written into a recipe step ("simmer for 10 minutes", "bake 1 hour 15 min")
 * so the recipe page can tag the step with a timer and cook mode can offer one.
 *
 * Steps are free text, so this is a best-effort read of common English and a handful of other
 * languages' unit words, not a parser. Ranges ("8-10 minutes") use their lower bound, the point
 * at which a cook would first check.
 */
export interface StepTimer {
  /** The duration as a clock reading, e.g. "8:00" or "1:15:00" */
  label: string;
  seconds: number;
}

const UNIT_SECONDS: [RegExp, number][] = [
  [/^(?:hours?|hrs?|stunden?|heures?|horas?|ore|ora|timmar|timer|uur)$/i, 3600],
  [/^(?:minutes?|mins?|minuten?|minutos?|minuti|minuter|minutter)$/i, 60],
  [/^(?:seconds?|secs?|sekunden?|secondes?|segundos?|secondi)$/i, 1],
];

const NUMBER = String.raw`\d+(?:[.,]\d+)?`;
const DURATION = new RegExp(
  String.raw`(${NUMBER})(?:\s*(?:-|–|—|to|bis|à|a)\s*${NUMBER})?\s*(?:(?:more|additional|extra|further|weitere)\s+)?([a-zA-Zäöüéà]+)\.?`,
  "g",
);
// what may sit between two parts of one duration, as in "1 hour and 30 minutes"
const JOINER = /^\s*(?:and|und|et|y|e|og|och|en)?\s*$/i;

function unitSeconds(word: string): number | null {
  for (const [pattern, seconds] of UNIT_SECONDS) {
    if (pattern.test(word)) {
      return seconds;
    }
  }
  return null;
}

export function formatTimer(totalSeconds: number): string {
  const seconds = Math.max(0, Math.round(totalSeconds));
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  return h ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

export function parseStepTimers(text: string | null | undefined): StepTimer[] {
  if (!text) {
    return [];
  }

  const timers: number[] = [];
  let lastEnd = -1;

  for (const match of text.matchAll(DURATION)) {
    const size = unitSeconds(match[2]!);
    if (size === null) {
      continue;
    }

    const amount = Number(match[1]!.replace(",", ".")) * size;
    const start = match.index!;
    const joinsPrevious = lastEnd >= 0 && JOINER.test(text.slice(lastEnd, start));

    if (joinsPrevious && timers.length) {
      timers[timers.length - 1]! += amount;
    }
    else {
      timers.push(amount);
    }
    lastEnd = start + match[0].length;
  }

  return timers
    .filter(seconds => seconds > 0)
    .map(seconds => ({ seconds, label: formatTimer(seconds) }));
}
