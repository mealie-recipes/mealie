import { describe, expect, test } from "vitest";
import { isSafeRedirectTarget } from "./redirect";

describe("isSafeRedirectTarget", () => {
  test("accepts an internal path", () => {
    expect(isSafeRedirectTarget("/g/home/r/some-recipe")).toBe(true);
  });

  test("rejects protocol-relative URLs", () => {
    expect(isSafeRedirectTarget("//evil.com")).toBe(false);
  });

  test("rejects backslash variants used to bypass same-origin checks", () => {
    expect(isSafeRedirectTarget("/\\evil.com")).toBe(false);
    expect(isSafeRedirectTarget("\\\\evil.com")).toBe(false);
  });

  test("rejects absolute URLs", () => {
    expect(isSafeRedirectTarget("https://evil.com")).toBe(false);
  });

  test("rejects empty or missing values", () => {
    expect(isSafeRedirectTarget("")).toBe(false);
    expect(isSafeRedirectTarget(null)).toBe(false);
    expect(isSafeRedirectTarget(undefined)).toBe(false);
  });
});
