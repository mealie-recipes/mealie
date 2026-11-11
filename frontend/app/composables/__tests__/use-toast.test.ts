import { describe, expect, test } from "vitest";
import { alert, toastAlert } from "../use-toast";

describe("alert", () => {
  test("keeps an error open for 10 seconds", () => {
    alert.error("Save failed");

    expect(toastAlert.timeout).toBe(10000);
  });

  test("keeps the timeout a caller passes for an error", () => {
    alert.error("Save failed", null, { timeout: 3000 });

    expect(toastAlert.timeout).toBe(3000);
  });

  test("keeps the default timeout for other alerts", () => {
    alert.success("Saved");

    expect(toastAlert.timeout).toBeUndefined();
  });
});
