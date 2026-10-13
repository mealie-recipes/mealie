import { describe, expect, test } from "vitest";
import { readableOn, withReadableOn } from "../readable-on";

describe("readableOn", () => {
  test.each([
    // the light theme's terracotta keeps white labels
    ["#C4502A", "#FFFFFF"],
    // the dark theme's brighter terracotta falls short of 4.5:1 with white, so it gets ink
    ["#E0683C", "#1C1B19"],
    ["#5E9BD1", "#1C1B19"],
    ["#1976D2", "#FFFFFF"],
    ["#000", "#FFFFFF"],
    ["fff", "#1C1B19"],
  ])("picks the readable label colour for %s", (color, expected) => {
    expect(readableOn(color)).toBe(expected);
  });

  test("falls back to white for anything that isn't a hex colour", () => {
    expect(readableOn("rgb(1, 2, 3)")).toBe("#FFFFFF");
  });
});

describe("withReadableOn", () => {
  test("adds a label colour for each named colour and leaves the rest alone", () => {
    const colors = withReadableOn({ warning: "#FF6D00", info: "#1976D2", surface: "#FFFFFF" }, ["warning", "info"]);

    expect(colors).toEqual({
      "warning": "#FF6D00",
      "on-warning": "#1C1B19",
      "info": "#1976D2",
      "on-info": "#FFFFFF",
      "surface": "#FFFFFF",
    });
  });
});
