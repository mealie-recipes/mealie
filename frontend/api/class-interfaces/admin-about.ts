import { BaseAPI } from "./_base";

const prefix = "/api";

const routes = {
  about: `${prefix}/admin/about`,
  aboutStatistics: `${prefix}/admin/about/statistics`,
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

export class AdminAboutAPI extends BaseAPI {
  async about() {
    return await this.requests.get<AdminAboutInfo>(routes.about);
  }

  async statistics() {
    return await this.requests.get(routes.aboutStatistics);
  }
}
