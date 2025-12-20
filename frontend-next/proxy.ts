import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { isTokenExpired, refreshBackendToken } from "@/lib/auth";
import { API_ROUTES } from "./lib/api/routes";

// 1. Define Public Pages (Frontend UI)
// These are likely hardcoded as they don't always align 1:1 with API_ROUTES
const PUBLIC_PAGES = ["/login", "/register", "/forgot-password"];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("mealie.access_token")?.value;

  // --------------------------------------------------------------------------
  // DETERMINING PUBLIC ROUTES
  // --------------------------------------------------------------------------
  const isStaticPublicApi = Object.values(
    API_ROUTES.PUBLIC_ROUTES.APP
  ).includes(pathname);

  const isDynamicPublicApi =
    pathname.startsWith("/api/auth") ||
    pathname.startsWith("/api/explore") ||
    pathname.startsWith("/api/validators") ||
    pathname.startsWith("/api/recipes/shared") ||
    pathname.startsWith("/api/users/register");

  const isPublic =
    PUBLIC_PAGES.includes(pathname) || isStaticPublicApi || isDynamicPublicApi;

  // --------------------------------------------------------------------------
  // AUTHENTICATION LOGIC
  // --------------------------------------------------------------------------
  const tokenExpired = isTokenExpired(token);
  const hasToken = !!token;

  // Redirect Authenticated Users away from Public Pages
  if (hasToken && !tokenExpired && PUBLIC_PAGES.includes(pathname)) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Protect Private Routes
  if (!isPublic) {
    if (!hasToken) {
      // If it's an API call, return 401 JSON instead of redirecting to HTML login page
      if (pathname.startsWith("/api/")) {
        return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
      }
      // If it's a Page load, redirect to Login
      return NextResponse.redirect(new URL("/login", request.url));
    }

    // Expired token handling...
    if (tokenExpired) {
      const refreshRes = await refreshBackendToken(request);

      if (!refreshRes) {
        // Refresh failed: Force Logout
        const response = NextResponse.redirect(new URL("/login", request.url));
        response.cookies.delete("mealie.access_token");
        response.cookies.delete("mealie.refresh_token");
        return response;
      }

      // Refresh success: Continue request with NEW token
      // Extract the new access token from Set-Cookie headers
      let newToken: string | undefined;
      const setCookies = refreshRes.headers.getSetCookie();

      for (const cookieHeader of setCookies) {
        // Parse cookie header to extract name and value
        const cookieParts = cookieHeader.split(";")[0]; // Get the name=value part
        const [name, value] = cookieParts.split("=");
        if (name?.trim() === "mealie.access_token") {
          newToken = value?.trim();
          break;
        }
      }

      // Create request with new Authorization header
      const requestHeaders = new Headers(request.headers);
      if (pathname.startsWith("/api/") && newToken) {
        requestHeaders.set("Authorization", `Bearer ${newToken}`);
      }
      const response = NextResponse.next({
        request: { headers: requestHeaders },
      });

      // Transfer all Set-Cookie headers to the outgoing response
      setCookies.forEach((c) => response.headers.append("Set-Cookie", c));

      return response;
    }
  }

  // 3. Inject Authorization Header for valid tokens (Public or Private routes)
  if (pathname.startsWith("/api/") && token) {
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("Authorization", `Bearer ${token}`);
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  return NextResponse.next();
}

export const config = {
  // Exclude static assets from middleware to improve performance
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
