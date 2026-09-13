export function normalizeMissingItemLimit(value: number | null | undefined): number {
  return Math.max(0, value ?? 0);
}
