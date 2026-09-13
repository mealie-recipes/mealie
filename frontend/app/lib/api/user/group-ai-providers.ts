import { BaseAPI } from "../base/base-clients";
import type { AIProviderCreate, AIProviderOut, AIProviderTestResult, AIProviderUpdate } from "~/lib/api/types/group";

const prefix = "/api/groups/ai-providers";

const routes = {
  providers: `${prefix}/providers`,
  providersId: (id: string) => `${prefix}/providers/${id}`,
  providersTest: `${prefix}/providers/test`,
  providersIdTest: (id: string) => `${prefix}/providers/${id}/test`,
};

export class AIProvidersAPI extends BaseAPI {
  async getOne(id: string) {
    return await this.requests.get<AIProviderOut>(routes.providersId(id));
  }

  async createOne(payload: AIProviderCreate) {
    return await this.requests.post<AIProviderOut>(routes.providers, payload);
  }

  async updateOne(id: string, payload: AIProviderUpdate) {
    return await this.requests.put<AIProviderOut, AIProviderUpdate>(routes.providersId(id), payload);
  }

  async deleteOne(id: string) {
    return await this.requests.delete<AIProviderOut>(routes.providersId(id));
  }

  async testOne(payload: AIProviderCreate) {
    return await this.requests.post<AIProviderTestResult>(routes.providersTest, payload);
  }

  async testSavedOne(id: string, overrides?: AIProviderUpdate & { apiKey?: string }) {
    return await this.requests.post<AIProviderTestResult, typeof overrides>(routes.providersIdTest(id), overrides);
  }
}
