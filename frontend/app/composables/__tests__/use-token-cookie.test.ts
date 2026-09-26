import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { getTokenCookieOptions, getTokenExpiry, nextRefreshDelay, readTokenCookie } from "../use-token-cookie";

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

  test("carries no max-age, since the server owns the cookie's lifetime", () => {
    stubNuxtApp(true);
    setLocation("https:");

    expect(getTokenCookieOptions()).not.toHaveProperty("maxAge");
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

const MAX_TIMEOUT_MS = 2 ** 31 - 1;
const MINUTE = 60 * 1000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

describe("nextRefreshDelay", () => {
  test("waits 60% of the remaining life, so each refresh lands well before expiry", () => {
    expect(nextRefreshDelay(10 * HOUR, 0)).toBe(6 * HOUR);
  });

  test("floors short delays, so a nearly-expired token can't spin the timer", () => {
    // 60% of 10s is 6s, which would re-arm faster than a refresh round-trip completes
    expect(nextRefreshDelay(10_000, 0)).toBe(30_000);
  });

  test("adds jitter on top, to spread simultaneous refreshes across tabs", () => {
    const base = nextRefreshDelay(10 * HOUR, 0)!;

    expect(nextRefreshDelay(10 * HOUR, 1)).toBe(base + 30_000);
    expect(nextRefreshDelay(10 * HOUR, 0.5)).toBe(base + 15_000);
  });

  test("never exceeds the setTimeout ceiling, even at maximum jitter", () => {
    // Regression: jitter used to be added *after* the clamp, so a long-lived token overflowed the
    // 32-bit delay, fired immediately, refreshed, and looped. Reachable at TOKEN_TIME >= ~992h.
    for (const remaining of [42 * DAY, 400 * DAY, Number.MAX_SAFE_INTEGER]) {
      expect(nextRefreshDelay(remaining, 1)).toBeLessThanOrEqual(MAX_TIMEOUT_MS);
    }
  });

  test("still schedules something for a very long-lived token", () => {
    // Clamped rather than skipped: refreshing a 400-day token early is harmless and keeps it sliding
    expect(nextRefreshDelay(400 * DAY, 0)).toBe(MAX_TIMEOUT_MS);
  });

  test("returns null once the token has expired, since there is nothing left to refresh with", () => {
    expect(nextRefreshDelay(0, 0)).toBeNull();
    expect(nextRefreshDelay(-1 * HOUR, 0)).toBeNull();
  });
});
