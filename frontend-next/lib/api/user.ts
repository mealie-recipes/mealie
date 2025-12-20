import { UserOut } from "../types/user/user";
import { apiRequest } from "./base/api-request-adapter";
import { BaseAPI } from "./base/base-api";
import { API_ROUTES } from "./routes";

/**
 * Authentication API class to handle auth-related requests
 */
export class UserAPI extends BaseAPI {
  constructor() {
    super(apiRequest);
  }

  /**
   * Fetches the current user's profile information
   * @returns a promise with UserOut data
   */
  async fetchSelf() {
    return await this.requests.get<UserOut>(API_ROUTES.USERS.CRUD.SELF);
  }
}

export const userApi = new UserAPI();
