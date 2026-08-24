import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { getTokenCookieOptions, getTokenExpiry, isRememberedSession, readTokenCookie } from "../use-token-cookie";

function setLocation(protocol: string) {
  Object.defineProperty(window, "location", {
    value: { ...window.location, protocol },
    configurable: true,
    writable: true,
  });
}

function setFramed(framed: boolean) {
  Object.defineProperty(window, "top", {
    value: framed ? ({} as Window) : window,
    configurable: true,
  });
}

function stubNuxtApp(production: boolean) {
  vi.stubGlobal("useNuxtApp", () => ({
    $appInfo: { production, tokenTime: 48 },
  }));
}

describe("getTokenCookieOptions", () => {
  beforeEach(() => {
    setFramed(false);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("top-level https connection gets a lax, non-partitioned cookie", () => {
    stubNuxtApp(true);
    setLocation("https:");
    setFramed(false);

    const options = getTokenCookieOptions();

    expect(options.secure).toBe(true);
    expect(options.sameSite).toBe("lax");
    expect(options.partitioned).toBe(false);
  });

  test("iframe-embedded https connection gets a none, partitioned cookie", () => {
    stubNuxtApp(true);
    setLocation("https:");
    setFramed(true);

    const options = getTokenCookieOptions();

    expect(options.secure).toBe(true);
    expect(options.sameSite).toBe("none");
    expect(options.partitioned).toBe(true);
  });

  test("insecure (http) connection stays lax and non-partitioned even when framed", () => {
    stubNuxtApp(true);
    setLocation("http:");
    setFramed(true);

    const options = getTokenCookieOptions();

    expect(options.secure).toBe(false);
    expect(options.sameSite).toBe("lax");
    expect(options.partitioned).toBe(false);
  });

  test("non-production build stays lax and non-partitioned even when framed over https", () => {
    stubNuxtApp(false);
    setLocation("https:");
    setFramed(true);

    const options = getTokenCookieOptions();

    expect(options.secure).toBe(false);
    expect(options.sameSite).toBe("lax");
    expect(options.partitioned).toBe(false);
  });

  test("omits max-age when no lifetime is given, producing a session cookie", () => {
    stubNuxtApp(true);
    setLocation("https:");

    expect(getTokenCookieOptions()).not.toHaveProperty("maxAge");
  });

  test("uses the granted lifetime when one is given, so a remembered session isn't cut short", () => {
    stubNuxtApp(true);
    setLocation("https:");

    const twoDays = 48 * 60 * 60;
    expect(getTokenCookieOptions(twoDays).maxAge).toBe(twoDays);
  });
});

function encodeToken(payload: Record<string, unknown>): string {
  const body = btoa(JSON.stringify(payload)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `header.${body}.signature`;
}

describe("getTokenExpiry", () => {
  test("reads exp as epoch milliseconds", () => {
    const exp = Math.floor(Date.now() / 1000) + 3600;
    expect(getTokenExpiry(encodeToken({ sub: "abc", exp }))).toBe(exp * 1000);
  });

  test("handles payloads whose base64url length needs padding", () => {
    // "rme" toggles the payload length, so between them these cover the padded and unpadded cases
    expect(getTokenExpiry(encodeToken({ exp: 1, rme: true }))).toBe(1000);
    expect(getTokenExpiry(encodeToken({ exp: 12, rme: false }))).toBe(12000);
  });

  test("returns null for a token with no exp", () => {
    expect(getTokenExpiry(encodeToken({ sub: "abc" }))).toBeNull();
  });

  test("returns null for a malformed token rather than throwing", () => {
    expect(getTokenExpiry("not-a-jwt")).toBeNull();
    expect(getTokenExpiry("header.@@@notbase64@@@.signature")).toBeNull();
    expect(getTokenExpiry("")).toBeNull();
  });
});

describe("isRememberedSession", () => {
  test("is true only when the token carries rme", () => {
    expect(isRememberedSession(encodeToken({ sub: "abc", rme: true }))).toBe(true);
    expect(isRememberedSession(encodeToken({ sub: "abc", rme: false }))).toBe(false);
    expect(isRememberedSession(encodeToken({ sub: "abc" }))).toBe(false);
  });

  test("is false for a malformed token rather than throwing", () => {
    expect(isRememberedSession("not-a-jwt")).toBe(false);
  });
});

describe("readTokenCookie", () => {
  afterEach(() => {
    document.cookie = "mealie.access_token=; max-age=0";
    document.cookie = "other=; max-age=0";
  });

  test("reads the named cookie", () => {
    document.cookie = "mealie.access_token=abc123";
    expect(readTokenCookie("mealie.access_token")).toBe("abc123");
  });

  test("does not match a different cookie whose name merely ends the same way", () => {
    document.cookie = "other=nope";
    expect(readTokenCookie("mealie.access_token")).toBeNull();
  });

  test("url-decodes the value", () => {
    document.cookie = `mealie.access_token=${encodeURIComponent("a.b+c/d")}`;
    expect(readTokenCookie("mealie.access_token")).toBe("a.b+c/d");
  });

  test("returns null when the cookie is absent", () => {
    expect(readTokenCookie("mealie.access_token")).toBeNull();
  });
});
