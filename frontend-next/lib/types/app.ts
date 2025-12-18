/**
 * Response type from /api/app/about endpoint
 */
export interface AppConfig {
  production: boolean;
  version: string;
  demoStatus: boolean;
  allowSignup: boolean;
  allowPasswordLogin: boolean;
  defaultGroupSlug: string;
  defaultHouseholdSlug: string;
  enableOidc: boolean;
  oidcRedirect: boolean;
  oidcProviderName: string;
  enableOpenai: boolean;
  enableOpenaiImageServices: boolean;
}

/**
 * Response type from /api/app/about/startup-info endpoint
 */
export interface StartupInfo {
  isFirstLogin: boolean;
  isDemoMode: boolean;
}
