import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { getCurrentWeekRange, navigateRange } from "./use-meal-plan-range";

// Local-time date formatting, since getCurrentWeekRange/navigateRange operate on
// local Date components (getDay/setDate), not UTC.
function toDateOnly(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

describe("getCurrentWeekRange", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  // 2024-01-17 is a Wednesday.
  test.each([
    [0, "2024-01-14", "2024-01-20"], // Sunday
    [1, "2024-01-15", "2024-01-21"], // Monday
    [2, "2024-01-16", "2024-01-22"], // Tuesday
    [3, "2024-01-17", "2024-01-23"], // Wednesday
    [4, "2024-01-11", "2024-01-17"], // Thursday
    [5, "2024-01-12", "2024-01-18"], // Friday
    [6, "2024-01-13", "2024-01-19"], // Saturday
  ])("startDay=%i returns week containing today", (startDay, expectedStart, expectedEnd) => {
    vi.setSystemTime(new Date(2024, 0, 17, 12, 0, 0));

    const [start, end] = getCurrentWeekRange(startDay);

    expect(toDateOnly(start)).toEqual(expectedStart);
    expect(toDateOnly(end)).toEqual(expectedEnd);
  });

  test("handles a month boundary", () => {
    // 2024-02-01 is a Thursday.
    vi.setSystemTime(new Date(2024, 1, 1, 12, 0, 0));

    const [start, end] = getCurrentWeekRange(0);

    expect(toDateOnly(start)).toEqual("2024-01-28");
    expect(toDateOnly(end)).toEqual("2024-02-03");
  });

  test("handles a year boundary", () => {
    // 2025-01-01 is a Wednesday.
    vi.setSystemTime(new Date(2025, 0, 1, 12, 0, 0));

    const [start, end] = getCurrentWeekRange(0);

    expect(toDateOnly(start)).toEqual("2024-12-29");
    expect(toDateOnly(end)).toEqual("2025-01-04");
  });

  test("returns today as start when startDay matches today", () => {
    // 2024-01-17 is a Wednesday (day 3).
    vi.setSystemTime(new Date(2024, 0, 17, 12, 0, 0));

    const [start, end] = getCurrentWeekRange(3);

    expect(toDateOnly(start)).toEqual("2024-01-17");
    expect(toDateOnly(end)).toEqual("2024-01-23");
  });
});

describe("navigateRange", () => {
  test("shifts forward by the period length for a 7-day range", () => {
    const start = new Date(2024, 0, 14);
    const end = new Date(2024, 0, 20);

    const [newStart, newEnd] = navigateRange(start, end, 1);

    expect(toDateOnly(newStart)).toEqual("2024-01-21");
    expect(toDateOnly(newEnd)).toEqual("2024-01-27");
  });

  test("shifts backward by the period length for a 7-day range", () => {
    const start = new Date(2024, 0, 14);
    const end = new Date(2024, 0, 20);

    const [newStart, newEnd] = navigateRange(start, end, -1);

    expect(toDateOnly(newStart)).toEqual("2024-01-07");
    expect(toDateOnly(newEnd)).toEqual("2024-01-13");
  });

  test("uses the actual period length for non-week-length ranges", () => {
    const start = new Date(2024, 0, 1);
    const end = new Date(2024, 0, 3);

    const [newStart, newEnd] = navigateRange(start, end, 1);

    expect(toDateOnly(newStart)).toEqual("2024-01-04");
    expect(toDateOnly(newEnd)).toEqual("2024-01-06");
  });

  test("handles a single-day range", () => {
    const start = new Date(2024, 0, 1);
    const end = new Date(2024, 0, 1);

    const [newStart, newEnd] = navigateRange(start, end, 1);

    expect(toDateOnly(newStart)).toEqual("2024-01-02");
    expect(toDateOnly(newEnd)).toEqual("2024-01-02");
  });

  test("handles a month boundary when navigating forward", () => {
    const start = new Date(2024, 0, 29);
    const end = new Date(2024, 1, 4);

    const [newStart, newEnd] = navigateRange(start, end, 1);

    expect(toDateOnly(newStart)).toEqual("2024-02-05");
    expect(toDateOnly(newEnd)).toEqual("2024-02-11");
  });
});
