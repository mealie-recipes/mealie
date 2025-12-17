import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 1. Check for the auth token cookie
  // Note: We haven't built the login yet, so this cookie won't exist.
  const token = request.cookies.get("mealie_token");
  const { pathname } = request.nextUrl;

  // 2. Define public routes (Login, Signup, etc.)
  const publicRoutes = ["/login", "/signup", "/forgot-password"];

  // 3. Logic: If no token and trying to access a protected route -> Redirect
  if (!token && !publicRoutes.includes(pathname)) {
    // Allows landing page to load for now, blocks everything else
    if (pathname === "/") return NextResponse.next();

    // Redirect to login
    // return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

// 4. Configure which paths the middleware runs on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
