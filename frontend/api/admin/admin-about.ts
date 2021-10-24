import { BaseAPI } from "../_base";

const prefix = "/api";

const routes = {
  about: `${prefix}/admin/about`,
  aboutStatistics: `${prefix}/admin/about/statistics`,
  check: `${prefix}/admin/about/check`,
};

export interface AdminAboutInfo {
  production: boolean;
  version: string;
  demoStatus: boolean;
  apiPort: number;
  apiDocs: boolean;
  dbType: string;
  dbUrl: string;
  defaultGroup: string;
}

export interface AdminStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalGroups: number;
  uncategorizedRecipes: number;
  untaggedRecipes: number;
}

export interface CheckAppConfig {
  emailReady: boolean;
  baseUrlSet: boolean;
}

export class AdminAboutAPI extends BaseAPI {
  async about() {
    return await this.requests.get<AdminAboutInfo>(routes.about);
  }

  async statistics() {
    return await this.requests.get(routes.aboutStatistics);
  }

  async checkApp() {
    return await this.requests.get<CheckAppConfig>(routes.check);
  }
}
