import { describe, expect, test } from "vitest";
import { cookingMethodOptions, getCookingMethodIcon, originalCookingMethodIcon } from "./cooking-methods";

describe("cooking method icons", () => {
  test("provides a distinct icon for every built-in cooking method", () => {
    expect(cookingMethodOptions.map(method => method.name)).toEqual([
      "Oven",
      "Air Fryer",
      "Slow Cooker",
      "Pressure Cooker",
      "Stovetop",
      "Grill / BBQ",
      "Microwave",
      "Smoker",
      "Sous Vide",
      "Rice Cooker",
    ]);
    expect(cookingMethodOptions.every(method => Boolean(method.icon))).toBe(true);
  });

  test("matches built-in methods without case sensitivity", () => {
    expect(getCookingMethodIcon("slow cooker")).toBe(getCookingMethodIcon("Slow Cooker"));
  });

  test("uses the original icon when no method is set", () => {
    expect(getCookingMethodIcon(null)).toBe(originalCookingMethodIcon);
  });

  test("uses a fallback icon for a custom method", () => {
    expect(getCookingMethodIcon("Solar Oven")).toBeTruthy();
    expect(getCookingMethodIcon("Solar Oven")).not.toBe(originalCookingMethodIcon);
  });
});
