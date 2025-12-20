import { AuthToken, OAuthCallback, OAuthProvider } from "../types/user/auth";
import {
  CreateUserRegistration,
  CredentialsRequest,
  UserOut,
} from "../types/user/user";
import { apiRequest } from "./base/api-request-adapter";
import { BaseAPI } from "./base/base-api";
import { API_ROUTES } from "./routes";

/**
 * Authentication API class to handle auth-related requests
 */
export class AuthAPI extends BaseAPI {
  constructor() {
    super(apiRequest);
  }

  /**
   * Logs in a user with the provided credentials
   * @param payload The user's login credentials
   * @returns The authentication token
   */
  async fetchToken(payload: CredentialsRequest) {
    const formData = new URLSearchParams();
    formData.append("username", payload.username);
    formData.append("password", payload.password);
    formData.append("remember_me", String(payload.remember_me || false));
    return await this.requests.post<AuthToken>(API_ROUTES.AUTH.TOKEN, formData);
  }

  /**
   * Fetches the OAuth provider information
   * @returns The OAuth provider details
   */
  async fetchOAuthProvider() {
    return await this.requests.get<OAuthProvider>(API_ROUTES.AUTH.OAUTH);
  }

  /**
   * Fetches OAuth callback information from the backend
   * @returns Promise with OAuthCallback data
   */
  async fetchOAuthCallback(searchParms: string) {
    return await this.requests.get<OAuthCallback>(
      API_ROUTES.AUTH.OAUTH_CALLBACK(searchParms)
    );
  }

  /**
   * Fetches authentication token refresh from the backend
   * @returns Promise with AuthRefresh data
   */
  async fetchAuthRefreshToken() {
    return await this.requests.post<AuthToken>(API_ROUTES.AUTH.REFRESH);
  }

  /**
   * Logs out the current user
   * @returns A promise indicating the logout operation result
   */
  async logout() {
    return await this.requests.post<{ message: string }>(
      API_ROUTES.AUTH.LOGOUT
    );
  }

  /**
   * Registers a new user with the provided details
   * @param payload The user's registration details
   * @returns A promise indicating the registration operation result
   */
  async registerUser(payload: CreateUserRegistration) {
    return await this.requests.post<UserOut>(
      API_ROUTES.USERS.REGISTRATION,
      payload
    );
  }
}

export const authApi = new AuthAPI();
