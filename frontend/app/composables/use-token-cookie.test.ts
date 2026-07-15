import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { getTokenCookieOptions } from "./use-token-cookie";

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
});
