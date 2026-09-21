import { beforeEach, describe, expect, test } from "vitest";
import { alertUnreportedError, toastAlert } from "../use-toast";

describe("alertUnreportedError", () => {
  beforeEach(() => {
    toastAlert.open = false;
    toastAlert.text = "";
    toastAlert.title = null;
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
    expect(toastAlert.title).toBeNull();
  });

  test("shows a plain string detail as the message, with the fallback as the title", () => {
    // e.g. a 400 with detail="Unsupported file extension"
    alertUnreportedError(
      { response: { data: { detail: "Unsupported file extension" } } },
      "fallback",
    );

    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toBe("Unsupported file extension");
    expect(toastAlert.title).toBe("fallback");
    expect(toastAlert.color).toBe("error");
  });

  test("falls back to the fallback text when the string detail is only whitespace", () => {
    alertUnreportedError({ response: { data: { detail: "   " } } }, "fallback");

    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toBe("fallback");
    expect(toastAlert.title).toBeNull();
  });

  test("falls back to the fallback text for an array detail", () => {
    // e.g. a 422 validation error
    alertUnreportedError(
      { response: { data: { detail: [{ msg: "x" }] } } } as unknown as Parameters<typeof alertUnreportedError>[0],
      "fallback",
    );

    expect(toastAlert.open).toBe(true);
    expect(toastAlert.text).toBe("fallback");
    expect(toastAlert.title).toBeNull();
  });
});
