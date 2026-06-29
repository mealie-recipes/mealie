import { BaseAPI } from "../base/base-clients";
import type { AIProviderCreate, AIProviderOut, AIProviderUpdate } from "~/lib/api/types/group";

const prefix = "/api/admin";

const routes = {
  providers: (groupId: string) => `${prefix}/groups/${groupId}/ai-providers/providers`,
  providersId: (groupId: string, providerId: string) => `${prefix}/groups/${groupId}/ai-providers/providers/${providerId}`,
};

export class AdminAIProvidersApi extends BaseAPI {
  async createProvider(groupId: string, payload: AIProviderCreate) {
    return await this.requests.post<AIProviderOut>(routes.providers(groupId), payload);
  }

  async getProvider(groupId: string, providerId: string) {
    return await this.requests.get<AIProviderOut>(routes.providersId(groupId, providerId));
  }

  async updateProvider(groupId: string, providerId: string, payload: AIProviderUpdate) {
    return await this.requests.put<AIProviderOut>(routes.providersId(groupId, providerId), payload);
  }

  async deleteProvider(groupId: string, providerId: string) {
    return await this.requests.delete<AIProviderOut>(routes.providersId(groupId, providerId));
  }
}
