import { addDays } from "date-fns";

/**
 * Returns the [start, end] of the current week, given the first day of the
 * week (0 = Sunday .. 6 = Saturday).
 */
export function getCurrentWeekRange(startDay: number): [Date, Date] {
  const today = new Date();
  const currentDay = today.getDay();
  let diff = currentDay - startDay;
  if (diff < 0) diff += 7;
  const start = new Date(today);
  start.setDate(today.getDate() - diff);
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return [start, end];
}

/**
 * Shifts a [start, end] range by its own length, in the given direction.
 */
export function navigateRange(start: Date, end: Date, direction: -1 | 1): [Date, Date] {
  const diffDays = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  const periodLength = diffDays + 1;
  const shift = periodLength * direction;
  return [addDays(start, shift), addDays(end, shift)];
}
