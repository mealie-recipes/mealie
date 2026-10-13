import { describe, expect, test } from "vitest";
import { contrast, readableOn, withReadableOn } from "../readable-on";

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

describe("default status colours", () => {
  // alerts and status text draw these colours as text on the page, the sidebar and cards
  test.each([
    ["light", ["#2A7531", "#1565C0", "#A84B0A", "#B3261E"], ["#FAF9F7", "#F3F1ED", "#FFFFFF"]],
    ["dark", ["#4CAF50", "#5E9BD1", "#FF6D00", "#F2706C"], ["#161513", "#1C1B19", "#1F1E1C"]],
  ])("meet 4.5:1 as text in the %s theme", (_, colors, backgrounds) => {
    for (const color of colors) {
      for (const background of backgrounds) {
        expect(contrast(color, background)).toBeGreaterThanOrEqual(4.5);
      }
    }
  });
});
