import { beforeEach, describe, expect, test } from "vitest";
import { alertUnreportedError, toastAlert } from "../use-toast";

describe("alertUnreportedError", () => {
  beforeEach(() => {
    toastAlert.open = false;
    toastAlert.text = "";
  });

  test("stays quiet when the interceptor already reported a Mealie error", () => {
    alertUnreportedError(
      { response: { data: { detail: { message: "Recipe already exists" } } } },
      "fallback",
    );

    expect(toastAlert.open).toBe(false);
  });

  test("reports a failure that carries no Mealie error body", () => {
    // e.g. a 413 raised by the web server in front of Mealie
    alertUnreportedError({ response: { data: undefined } }, "fallback");

    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toBe("fallback");
  });

  test("reports a failure with no response at all", () => {
    // e.g. a dropped connection or a timeout
    alertUnreportedError({}, "fallback");

    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toBe("fallback");
  });
});
