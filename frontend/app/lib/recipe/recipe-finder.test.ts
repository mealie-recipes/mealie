import { describe, expect, it } from "vitest";

import { normalizeMissingItemLimit } from "./recipe-finder";

describe("normalizeMissingItemLimit", () => {
  it("preserves non-negative limits", () => {
    expect(normalizeMissingItemLimit(0)).toBe(0);
    expect(normalizeMissingItemLimit(20)).toBe(20);
  });

  it("clamps negative limits to zero", () => {
    expect(normalizeMissingItemLimit(-1)).toBe(0);
  });

  it("normalizes an empty input to zero", () => {
    expect(normalizeMissingItemLimit(null)).toBe(0);
    expect(normalizeMissingItemLimit(undefined)).toBe(0);
  });
});
