import { NextRequest, NextResponse } from "next/server";
import { API_ROUTES } from "./api/routes";
import { fetchAuthRefresh } from "./api/users/auth";

// Standardize expiration buffer (e.g., refresh if expiring in < 24h)
const EXPIRATION_BUFFER_SEC = 86400;

/**
 * Checks if a JWT is expired or about to expire
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
 * Server-side refresh: Calls backend using existing cookies
 */
export async function refreshBackendToken(
  req: NextRequest
): Promise<NextResponse | null> {
  const backendUrl = process.env.BACKEND_URL || "http://localhost:9000";

  try {
    const res = await fetch(`${backendUrl}${API_ROUTES.AUTH.REFRESH}`, {
      method: "POST",
      headers: {
        Cookie: req.headers.get("cookie") || "",
      },
    });

    if (!res.ok) return null;

    const data = await res.json();

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
    console.error("Token refresh failed", e);
    return null;
  }
}
