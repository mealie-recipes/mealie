import { describe, expect, test } from "vitest";
import { sanitizeInlineHtml } from "./inline";

// Payload from GHSA-h73g-85mv-f42f: a full-screen overlay with a phishing link.
const OVERLAY_PAYLOAD = `<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;background:#fff">
<p>This recipe has been removed. <a href="https://attacker.example/login">Click here</a>.</p>
</div><a name="recipe"></a><img src="https://attacker.example/beacon.png">`;

describe("sanitizeInlineHtml", () => {
  test("returns empty string for nullish input", () => {
    expect(sanitizeInlineHtml(null)).toEqual("");
    expect(sanitizeInlineHtml(undefined)).toEqual("");
    expect(sanitizeInlineHtml("")).toEqual("");
  });

  test("keeps fraction formatting", () => {
    expect(sanitizeInlineHtml("1<sup>1</sup><span>&frasl;</span><sub>2</sub>")).toEqual(
      "1<sup>1</sup><span>⁄</span><sub>2</sub>",
    );
  });

  test("keeps emphasis tags", () => {
    expect(sanitizeInlineHtml("<strong>a</strong> <b>b</b> <i>c</i> <q>d</q>")).toEqual(
      "<strong>a</strong> <b>b</b> <i>c</i> <q>d</q>",
    );
  });

  test("strips block elements, links, images, and styles from the overlay payload", () => {
    const html = sanitizeInlineHtml(OVERLAY_PAYLOAD);
    for (const fragment of ["<div", "<p", "<a", "<img", "style", "href", "position", "attacker.example"]) {
      expect(html).not.toContain(fragment);
    }
    expect(html).toContain("This recipe has been removed.");
  });

  test("drops attributes on allowed tags", () => {
    expect(sanitizeInlineHtml("<span class=\"position-fixed\" style=\"color:red\" onclick=\"x()\">a</span>")).toEqual(
      "<span>a</span>",
    );
  });
});
