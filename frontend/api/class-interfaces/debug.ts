import { BaseAPI } from "./_base";

export interface AppStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalGroups: number;
  uncategorizedRecipes: number;
  untaggedRecipes: number;
}

const prefix = "/api";

const routes = {
  debugVersion: `${prefix}/debug/version`,
  debug: `${prefix}/debug`,
  debugStatistics: `${prefix}/debug/statistics`,
  debugLastRecipeJson: `${prefix}/debug/last-recipe-json`,
  debugLog: `${prefix}/debug/log`,

  debugLogNum: (num: number) => `${prefix}/debug/log/${num}`,
};

export class DebugAPI extends BaseAPI {
  /** Returns the current version of mealie
   */
  async getMealieVersion() {
    return await this.requests.get(routes.debugVersion);
  }

  /** Returns general information about the application for debugging
   */
  async getDebugInfo() {
    return await this.requests.get(routes.debug);
  }

  async getAppStatistics() {
    return await this.requests.get<AppStatistics>(routes.debugStatistics);
  }

  /** Doc Str
   */
  async getLog(num: number) {
    return await this.requests.get(routes.debugLogNum(num));
  }

  /** Returns a token to download a file
   */
  async getLogFile() {
    return await this.requests.get(routes.debugLog);
  }
}
