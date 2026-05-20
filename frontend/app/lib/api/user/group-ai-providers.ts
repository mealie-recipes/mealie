import { BaseAPI } from "../base/base-clients";
import type { AIProviderCreate, AIProviderOut, AIProviderUpdate } from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  providers: `${prefix}/ai-providers/providers`,
  providersId: (id: string) => `${prefix}/ai-providers/providers/${id}`,
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
}
