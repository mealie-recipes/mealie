/**
 * Cookie options used to clear the session token.
 *
 * The server sets the cookie; the client only ever removes it, on logout or a dead session. A cookie
 * is matched for removal by name and path, but these have to line up with what the server sent for
 * the embedded (SameSite=None) case to clear reliably.
 */
export function getTokenCookieOptions() {
  const { $appInfo } = useNuxtApp();

  const isSecureConnection = $appInfo.production && window?.location?.protocol === "https:";
  const isEmbedded = isSecureConnection && window?.self !== window?.top;

  return {
    secure: isSecureConnection,
    sameSite: (isEmbedded ? "none" : "lax") as "none" | "lax",
  };
}

/**
 * Reads a JWT's claims without verifying its signature.
 *
 * Only used for claims the server itself put there and the client needs to act on locally — when to
 * refresh, and whether to persist the cookie. Nothing is trusted for authorization.
 */
function decodeTokenPayload(token: string): Record<string, unknown> | null {
  const payload = token.split(".")[1];
  if (!payload) {
    return null;
  }

  try {
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
    const claims = JSON.parse(atob(padded));

    return typeof claims === "object" && claims !== null ? claims : null;
  }
  catch {
    return null;
  }
}

/** Epoch milliseconds at which a token expires, or null when it carries no readable `exp`. */
export function getTokenExpiry(token: string): number | null {
  const exp = decodeTokenPayload(token)?.exp;
  return typeof exp === "number" ? exp * 1000 : null;
}

/**
 * Reads the token straight out of `document.cookie`.
 *
 * `useCookie` would allocate a BroadcastChannel and a watcher on every call, which is wasteful on
 * hot paths like the axios request interceptor that only ever need the current value.
 */
export function readTokenCookie(name: string): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}=([^;]*)`));
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

/** Refresh once this fraction of the token's remaining life has elapsed. */
const REFRESH_AFTER_FRACTION = 0.6;
/** Never schedule a refresh tighter than this, so a near-expired token can't spin the timer. */
const MIN_REFRESH_DELAY_MS = 30_000;
/** Spread concurrent refreshes across tabs so they don't all fire on the same millisecond. */
const REFRESH_JITTER_MS = 30_000;
/**
 * setTimeout stores its delay as a 32-bit signed integer, so anything longer overflows and fires
 * straight away instead of waiting. There is no constant exposed for this — `Number.MAX_SAFE_INTEGER`
 * is a different limit entirely — so the ceiling is spelled out. Waiting out a token longer than
 * ~24.8 days just means refreshing it early, which costs one request and keeps the session sliding.
 */
const MAX_TIMEOUT_MS = 2 ** 31 - 1;

/**
 * How long to wait before refreshing a token with `remainingMs` of life left, or null when there is
 * nothing worth scheduling.
 *
 * Derived from the time remaining rather than a fixed interval, so it self-corrects when a timer
 * fires late — after the device sleeps, or while the tab was backgrounded and throttled.
 *
 * `jitter` is injectable so the result can be asserted; callers should leave it to `Math.random`.
 */
export function nextRefreshDelay(remainingMs: number, jitter: number = Math.random()): number | null {
  if (remainingMs <= 0) {
    // Already expired. Refreshing needs a token the server still accepts, so there is nothing to be
    // done here — the next request's 401 sends the user to the login page.
    return null;
  }

  // Jitter goes on before the clamp, not after: adding it to an already-clamped delay can push the
  // total past the 32-bit ceiling, which overflows to "fire now" and spins into a refresh loop.
  const target = Math.max(remainingMs * REFRESH_AFTER_FRACTION, MIN_REFRESH_DELAY_MS)
    + jitter * REFRESH_JITTER_MS;

  return Math.min(target, MAX_TIMEOUT_MS);
}
