import { describe, expect, it } from "vitest";

import { textColorForBackground } from "./text-color";

describe("textColorForBackground", () => {
  it("uses black text on a light background", () => {
    expect(textColorForBackground("#ffffff")).toBe("#000000");
    expect(textColorForBackground("#f00")).toBe("#ffffff");
    expect(textColorForBackground("#ff0000")).toBe("#ffffff");
  });

  it("uses white text on a dark background", () => {
    expect(textColorForBackground("#000000")).toBe("#ffffff");
    expect(textColorForBackground("#000")).toBe("#ffffff");
  });

  it("returns undefined for missing or malformed colors", () => {
    expect(textColorForBackground(undefined)).toBeUndefined();
    expect(textColorForBackground("")).toBeUndefined();
    expect(textColorForBackground("black")).toBeUndefined();
    expect(textColorForBackground("#gghhhh")).toBeUndefined();
  });
});
