import { NextResponse } from "next/server";

/**
 * Mock API endpoint for /api/app/about
 * In production, this will be proxied to the backend via next.config.ts
 * This is for testing/development purposes only
 */
export async function GET() {
  // Default configuration showing all features
  const config = {
    production: false,
    version: "1.0.0",
    demoStatus: true,
    allowSignup: true,
    allowPasswordLogin: true,
    defaultGroupSlug: "home",
    defaultHouseholdSlug: "home",
    enableOidc: false,
    oidcRedirect: false,
    oidcProviderName: "SSO",
    enableOpenai: false,
    enableOpenaiImageServices: false,
  };

  return NextResponse.json(config);
}
