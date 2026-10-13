import { describe, expect, test } from "vitest";
import { formatTimer, parseStepTimers } from "../use-step-timers";

describe("formatTimer", () => {
  test.each([
    [0, "0:00"],
    [45, "0:45"],
    [480, "8:00"],
    [4500, "1:15:00"],
  ])("formats %j seconds as %j", (seconds, expected) => {
    expect(formatTimer(seconds)).toBe(expected);
  });
});

describe("parseStepTimers", () => {
  test.each([
    ["Cook, stirring, until soft, about 8 minutes.", ["8:00"]],
    ["Simmer 10 min. until thickened", ["10:00"]],
    ["Bake for 1 hour 15 minutes", ["1:15:00"]],
    ["Bake for 1 hour and 15 minutes", ["1:15:00"]],
    ["Rest 1.5 hours", ["1:30:00"]],
    ["Fry 30 seconds per side", ["0:30"]],
    ["Roast 8-10 minutes, flip, then roast 5 more minutes", ["8:00", "5:00"]],
    ["Roast 8 to 10 minutes", ["8:00"]],
    ["Köcheln lassen, etwa 15 Minuten", ["15:00"]],
  ])("finds the timers in %j", (text, expected) => {
    expect(parseStepTimers(text).map(timer => timer.label)).toEqual(expected);
  });

  test.each([
    "Heat 2 tbsp olive oil over medium heat.",
    "Preheat the oven to 350 degrees.",
    "Crack 6 eggs into the sauce.",
    "",
  ])("finds nothing in %j", (text) => {
    expect(parseStepTimers(text)).toEqual([]);
  });

  test("handles missing text", () => {
    expect(parseStepTimers(null)).toEqual([]);
    expect(parseStepTimers(undefined)).toEqual([]);
  });

  test("reports seconds alongside the label", () => {
    expect(parseStepTimers("wait 2 minutes")).toEqual([{ seconds: 120, label: "2:00" }]);
  });
});
