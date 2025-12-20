/**
 * Response type from /api/auth/token endpoint
 */
export interface AuthToken {
  access_token: string;
  token_type: string;
}

/**
 * Response type from /api/auth/oauth endpoint
 */
export interface OAuthProvider {
  // Unknown structure, using index signature
  [key: string]: any;
}

/**
 * Response type from /api/auth/oauth/callback endpoint
 */
export interface OAuthCallback {
  // Unknown structure, using index signature
  [key: string]: any;
}

/**
 * Response type from /api/auth/refresh endpoint
 */
export interface AuthRefresh {
  access_token: string;
  token_type: string;
}

/**
 * Response type from /api/auth/logout endpoint
 */
export interface AuthLogout {
  message: string;
}
