import { BaseAPI } from "../base/base-clients";
import type { AppTheme } from "~/lib/api/types/non-generated";

const prefix = "/api";

const routes = {
  theme: `${prefix}/admin/theme`,
};

export class AdminThemeAPI extends BaseAPI {
  async get() {
    return await this.requests.get<AppTheme>(routes.theme);
  }

  async update(payload: AppTheme) {
    return await this.requests.put<AppTheme>(routes.theme, payload);
  }

  async reset() {
    return await this.requests.delete(routes.theme);
  }
}
