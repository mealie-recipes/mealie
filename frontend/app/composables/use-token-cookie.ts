/**
 * Cookie options for the session token.
 *
 * Pass the lifetime the backend granted this token to get a persistent cookie ("remember me").
 * Omit it for a session cookie, which the browser drops when it closes. There is deliberately no
 * `TOKEN_TIME` fallback: guessing the lifetime is what used to expire the cookie while the token it
 * held was still valid.
 */
export function getTokenCookieOptions(maxAgeSeconds?: number) {
  const { $appInfo } = useNuxtApp();

  const isSecureConnection = $appInfo.production && window?.location?.protocol === "https:";
  const isEmbedded = isSecureConnection && window?.self !== window?.top;

  return {
    ...(maxAgeSeconds === undefined ? {} : { maxAge: maxAgeSeconds }),
    secure: isSecureConnection,
    sameSite: (isEmbedded ? "none" : "lax") as "none" | "lax",
    partitioned: isEmbedded,
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
 * Whether this session should outlive the browser session.
 *
 * Set from the "remember me" checkbox at login and carried across refreshes, so a remembered session
 * keeps its persistent cookie instead of quietly becoming one that dies on the next browser close.
 */
export function isRememberedSession(token: string): boolean {
  return decodeTokenPayload(token)?.rme === true;
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
