import { NextRequest, NextResponse } from "next/server";
import { API_ROUTES } from "./api/routes";

// Standardize expiration buffer (e.g., refresh if expiring in < 15 minutes)
const EXPIRATION_BUFFER_SEC = 900;

/**
 * Determine whether a JWT is expired or will expire within the configured buffer.
 *
 * Treats a missing or malformed token as expired. If the token payload contains no
 * `exp` claim the token is considered valid.
 *
 * @param token - The JWT string to inspect.
 * @returns `true` if the token is expired or will expire within EXPIRATION_BUFFER_SEC, `false` otherwise.
 */
export function isTokenExpired(token?: string): boolean {
  if (!token) return true;
  try {
    const [, payload] = token.split(".");
    if (!payload) return true;
    const decoded = JSON.parse(atob(payload));

    // If no exp, assume valid; otherwise check against now + buffer
    if (!decoded.exp) return false;
    return Date.now() / 1000 > decoded.exp - EXPIRATION_BUFFER_SEC;
  } catch {
    return true;
  }
}

/**
 * Performs a server-side token refresh by POSTing the incoming request's cookies to the backend refresh endpoint.
 *
 * @param req - The incoming NextRequest; its Cookie header will be forwarded to the backend.
 * @returns A NextResponse containing the backend's JSON body and any forwarded `Set-Cookie` headers, or `null` if the refresh failed, timed out, or the response was not valid JSON.
 */
export async function refreshBackendToken(
  req: NextRequest
): Promise<NextResponse | null> {
  const backendUrl = process.env.BACKEND_URL || "http://localhost:9000";
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000); // 5-second timeout

  try {
    const res = await fetch(`${backendUrl}${API_ROUTES.AUTH.REFRESH}`, {
      method: "POST",
      headers: {
        Cookie: req.headers.get("cookie") || "",
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      console.error(`Token refresh failed with status ${res.status}`);
      return null;
    }

    // Validate content-type is JSON before attempting to parse
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      console.error(
        `Token refresh returned non-JSON response: ${
          contentType || "no content-type"
        }`
      );
      return null;
    }

    let data;
    try {
      data = await res.json();
    } catch (parseError) {
      console.error(
        "Failed to parse token refresh response as JSON",
        parseError
      );
      return null;
    }

    // Create a new response to hold the new cookies
    const nextRes = new NextResponse(JSON.stringify(data));

    // Copy Set-Cookie headers from backend to our Next.js response
    // This effectively "passthrough" the new cookies to the browser
    const setCookies = res.headers.getSetCookie();
    for (const cookie of setCookies) {
      nextRes.headers.append("Set-Cookie", cookie);
    }

    return nextRes;
  } catch (e) {
    clearTimeout(timeoutId);
    if (e instanceof Error && e.name === "AbortError") {
      console.error("Token refresh request timed out (5s exceeded)");
    } else {
      console.error("Token refresh failed", e);
    }
    return null;
  }
}
