import { describe, expect, test } from "vitest";
import { durationUnitLabel, formatDuration, recipeTimeDisplay } from "../use-recipe-time";

describe("formatDuration", () => {
  test.each([
    [60, "1 minute"],
    [1800, "30 minutes"],
    [3600, "1 hour"],
    [5400, "1 hour 30 minutes"],
    [90, "1 minute 30 seconds"],
    [93600, "1 day 2 hours"],
  ])("formats %j seconds as %j", (seconds, expected) => {
    expect(formatDuration(seconds, "en-US")).toBe(expected);
  });

  test("is localized", () => {
    // joined however the locale joins units, which varies with the ICU version
    const formatted = formatDuration(5400, "de-DE");
    expect(formatted).toMatch(/^1 Stunde\b/);
    expect(formatted).toMatch(/\b30 Minuten$/);
  });
});

describe("durationUnitLabel", () => {
  test.each([
    ["hour", "hr"],
    ["minute", "min"],
  ] as const)("names %j as %j", (unit, expected) => {
    expect(durationUnitLabel(unit, "en-US")).toBe(expected);
  });
});

describe("recipeTimeDisplay", () => {
  test("combines the structured time with the text", () => {
    expect(recipeTimeDisplay(10800, "plus overnight", "en-US")).toBe("3 hours plus overnight");
  });

  test.each([
    [5400, null, "1 hour 30 minutes"],
    [5400, " ", "1 hour 30 minutes"],
    [null, "overnight", "overnight"],
    [undefined, "overnight", "overnight"],
    [0, "overnight", "overnight"],
    [null, null, ""],
    [null, "", ""],
  ])("shows whichever is set for %j seconds and %j", (seconds, text, expected) => {
    expect(recipeTimeDisplay(seconds, text, "en-US")).toBe(expected);
  });
});
