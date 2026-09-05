import { beforeEach, describe, expect, test } from "vitest";
import { useUnitSystem } from "../use-unit-system";

describe("useUnitSystem", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("shows recipes as written until the reader opts in", () => {
    const { unitSystem, isConverting } = useUnitSystem();

    expect(unitSystem.value).toBeNull();
    expect(isConverting.value).toBe(false);
  });

  test("nothing is inferred from the locale", () => {
    // deliberately no locale lookup: a wrong guess would silently rewrite every quantity
    expect(useUnitSystem().unitSystem.value).toBeNull();
  });

  test.each(["metric", "us", "imperial"] as const)("%s can be chosen", (system) => {
    const { unitSystem, isConverting } = useUnitSystem();
    unitSystem.value = system;

    expect(unitSystem.value).toBe(system);
    expect(isConverting.value).toBe(true);
  });

  test("the choice survives a reload", () => {
    useUnitSystem().unitSystem.value = "imperial";

    expect(useUnitSystem().unitSystem.value).toBe("imperial");
  });

  test("showAsWritten goes back to the authored units", () => {
    const { unitSystem, isConverting, showAsWritten } = useUnitSystem();
    unitSystem.value = "metric";
    showAsWritten();

    expect(unitSystem.value).toBeNull();
    expect(isConverting.value).toBe(false);
  });
});
