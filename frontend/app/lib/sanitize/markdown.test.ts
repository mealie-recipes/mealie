import { describe, expect, test } from "vitest";
import { sanitizeMarkdownHtml } from "./markdown";

describe("sanitizeMarkdownHtml", () => {
  test("returns empty string for nullish input", () => {
    expect(sanitizeMarkdownHtml(null)).toEqual("");
    expect(sanitizeMarkdownHtml(undefined)).toEqual("");
    expect(sanitizeMarkdownHtml("")).toEqual("");
  });

  test("keeps allowed formatting tags", () => {
    const html = sanitizeMarkdownHtml("<p>Mix <strong>flour</strong> and <em>water</em></p>");
    expect(html).toContain("<strong>flour</strong>");
    expect(html).toContain("<em>water</em>");
  });

  test("strips script tags and event handlers", () => {
    const html = sanitizeMarkdownHtml("<p onclick=\"alert(1)\">hi</p><script>alert(1)</script>");
    expect(html).not.toContain("script");
    expect(html).not.toContain("onclick");
    expect(html).not.toContain("alert");
  });

  test("strips img onerror payloads", () => {
    const html = sanitizeMarkdownHtml("<img src=x onerror=alert(1)>");
    expect(html).not.toContain("onerror");
  });

  // Form controls must never render in user content.
  test("strips form, input, and button elements", () => {
    const html = sanitizeMarkdownHtml("<form action=/x><input name=p><button>go</button></form>");
    expect(html).not.toContain("<form");
    expect(html).not.toContain("<input");
    expect(html).not.toContain("<button");
  });

  test("strips class attributes so utility classes can't build an overlay", () => {
    const html = sanitizeMarkdownHtml("<div class=\"position-fixed top-0 left-0 w-100 h-screen bg-white\">x</div>");
    expect(html).not.toContain("class");
    expect(html).not.toContain("position-fixed");
  });

  test("strips positioning styles and keeps allowed ones", () => {
    const html = sanitizeMarkdownHtml("<div style=\"position:fixed;top:0;z-index:999999;color:red\">x</div>");
    expect(html).not.toContain("position");
    expect(html).not.toContain("z-index");
    expect(html).toContain("color:red");
  });

  test("prefixes name attributes to prevent DOM clobbering", () => {
    const html = sanitizeMarkdownHtml("<a name=\"recipe\"></a><img name=\"config\" src=\"/x.png\">");
    expect(html).toContain("name=\"user-content-recipe\"");
    expect(html).toContain("name=\"user-content-config\"");
  });

  test("strips javascript: links", () => {
    const html = sanitizeMarkdownHtml("<a href=\"javascript:alert(1)\">x</a>");
    expect(html).not.toContain("javascript");
  });

  test("strips iframes when no allowed hosts are configured", () => {
    const html = sanitizeMarkdownHtml("<iframe src=\"https://evil.example/x\"></iframe>", []);
    expect(html).not.toContain("<iframe");
  });

  test("strips iframes whose src host is not allowlisted", () => {
    const html = sanitizeMarkdownHtml(
      "<iframe src=\"https://evil.example/x\"></iframe>",
      ["youtube.com"],
    );
    expect(html).not.toContain("<iframe");
  });

  test("strips non-https iframes even for an allowlisted host", () => {
    const html = sanitizeMarkdownHtml(
      "<iframe src=\"http://www.youtube.com/embed/abc\"></iframe>",
      ["youtube.com"],
    );
    expect(html).not.toContain("<iframe");
  });

  test("keeps iframes from an allowlisted host (incl. subdomains)", () => {
    const html = sanitizeMarkdownHtml(
      "<iframe src=\"https://www.youtube.com/embed/abc\"></iframe>",
      ["youtube.com"],
    );
    expect(html).toContain("<iframe");
    expect(html).toContain("https://www.youtube.com/embed/abc");
  });

  test("does not allow a lookalike host to pass the suffix check", () => {
    const html = sanitizeMarkdownHtml(
      "<iframe src=\"https://notyoutube.com/embed/abc\"></iframe>",
      ["youtube.com"],
    );
    expect(html).not.toContain("<iframe");
  });
});
