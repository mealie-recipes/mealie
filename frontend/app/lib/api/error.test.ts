import { describe, expect, test } from "vitest";
import { getApiErrorMessage } from "./error";

describe("getApiErrorMessage", () => {
  test("extracts a string detail", () => {
    const error = { response: { data: { detail: "Invalid group token" } } };

    expect(getApiErrorMessage(error)).toBe("Invalid group token");
  });

  test("extracts a nested detail message", () => {
    const error = { response: { data: { detail: { message: "Username already exists" } } } };

    expect(getApiErrorMessage(error)).toBe("Username already exists");
  });

  test.each([
    null,
    {},
    { response: null },
    { response: { data: null } },
    { response: { data: { detail: [{ message: "Validation error" }] } } },
  ])("returns null for an unsupported error shape", (error) => {
    expect(getApiErrorMessage(error)).toBeNull();
  });
});
