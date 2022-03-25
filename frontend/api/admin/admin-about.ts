import { BaseAPI } from "../_base";
import { AdminAboutInfo } from "~/types/api-types/admin";

const prefix = "/api";

const routes = {
  about: `${prefix}/admin/about`,
  aboutStatistics: `${prefix}/admin/about/statistics`,
  check: `${prefix}/admin/about/check`,
};


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
  isSiteSecure: boolean;
  isUpToDate: boolean;
  ldapReady: boolean;
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
