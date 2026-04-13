import { BaseAPI } from "../base/base-clients";
import type { MealieAnalytics } from "~/lib/api/types/analytics";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/analytics`,
};

export class AdminAnalyticsApi extends BaseAPI {
  async getAnalytics() {
    return await this.requests.get<MealieAnalytics>(routes.base);
  }
}
