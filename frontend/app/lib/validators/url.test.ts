import { describe, expect, test } from "vitest";
import { isHttpUrl } from "./url";

describe("isHttpUrl", () => {
  test.each(["https://example.com/recipe", "http://example.com", "HTTPS://EXAMPLE.COM"])("accepts %s", (url) => {
    expect(isHttpUrl(url)).toBe(true);
  });

  test.each([
    null,
    undefined,
    "",
    "javascript:alert(1)",
    " javascript:alert(1)",
    "JaVaScRiPt:alert(1)",
    "java\tscript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
    "/relative/path",
    "example.com",
  ])("rejects %s", (url) => {
    expect(isHttpUrl(url)).toBe(false);
  });
});
