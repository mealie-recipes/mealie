import { describe, expect, test, vi } from "vitest";
import { truncateText } from "./text";

describe("truncateText", () => {
  test("returns short text unchanged", () => {
    expect(truncateText("Dinner")).toEqual("Dinner");
  });

  test("truncates long text with clamp", () => {
    expect(truncateText("a".repeat(25))).toEqual(`${"a".repeat(20)}...`);
  });

  test("respects custom length and clamp", () => {
    expect(truncateText("abcdef", 3, "~")).toEqual("abc~");
  });

  test("does not clamp text exactly at the length boundary", () => {
    expect(truncateText("abcde", 5)).toEqual("abcde");
    expect(truncateText("abcdef", 5)).toEqual("abcde...");
  });

  // Markup in the input must be treated as plain text and never parsed into the live document.
  test("does not parse or execute HTML payloads", () => {
    const createElement = vi.spyOn(document, "createElement");
    const payload = "<img src=x onerror=alert(1)>";

    const result = truncateText(payload);

    // The payload is returned verbatim (truncated only by length), proving it is treated as text.
    expect(result).toEqual(`${payload.slice(0, 20)}...`);
    // No DOM element is constructed, so no <img> can fire its onerror handler.
    expect(createElement).not.toHaveBeenCalled();
    createElement.mockRestore();
  });
});
