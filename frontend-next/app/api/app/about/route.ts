import { NextResponse } from "next/server";

/**
 * Provide a mock response for GET /api/app/about containing the default application configuration.
 *
 * Used for development and testing; in production this route is expected to be proxied to the backend via next.config.ts.
 *
 * @returns The default configuration object with fields:
 * `production`, `version`, `demoStatus`, `allowSignup`, `allowPasswordLogin`,
 * `defaultGroupSlug`, `defaultHouseholdSlug`, `enableOidc`, `oidcRedirect`,
 * `oidcProviderName`, `enableOpenai`, and `enableOpenaiImageServices`.
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