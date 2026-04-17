import { BaseAPI } from "../base/base-clients";
import type {
  RecommendationDismissIn,
  RecommendationPreferencesIn,
  RecommendationResult,
  RecommendationStatus,
} from "../types/recommendations";

const prefix = "/api/recommendations";

const routes = {
  base: prefix,
  status: `${prefix}/status`,
  preferences: `${prefix}/preferences`,
  dismiss: `${prefix}/dismiss`,
};

export class RecommendationApi extends BaseAPI {
  async getStatus() {
    return await this.requests.get<RecommendationStatus>(routes.status);
  }

  async getRecommendations() {
    return await this.requests.get<RecommendationResult>(routes.base);
  }

  async setPreferences(payload: RecommendationPreferencesIn) {
    return await this.requests.post<{ status: string }, RecommendationPreferencesIn>(routes.preferences, payload);
  }

  async dismiss(payload: RecommendationDismissIn) {
    return await this.requests.post<{ status: string }, RecommendationDismissIn>(routes.dismiss, payload);
  }
}
