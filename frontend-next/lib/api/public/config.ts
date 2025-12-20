// src/lib/api/app-system-api.ts
import { apiRequest } from "../base/api-request-adapter";
import { BaseAPI } from "../base/base-api";
import { API_ROUTES } from "../routes";
import type { AppConfig, StartupInfo, Theme } from "@/lib/types/app";

export class ConfigAPI extends BaseAPI {
  constructor() {
    super(apiRequest);
  }
  /**
   * Fetches application configuration from the backend
   * @returns Promise with AppConfig data
   */
  async getAppConfig() {
    return this.requests.get<AppConfig>(API_ROUTES.APP.CONFIG, {});
  }

  /**
   * Fetches startup information from the backend
   * @returns Promise with StartupInfo data
   */
  async getStartupInfo() {
    return this.requests.get<StartupInfo>(API_ROUTES.APP.STARTUP_INFO);
  }

  /**
   * Fetches theme information from the backend
   * @returns Promise with Theme data
   */
  async getTheme() {
    return this.requests.get<Theme>(API_ROUTES.APP.THEME);
  }
}

// Create a singleton instance
export const configApi = new ConfigAPI();
