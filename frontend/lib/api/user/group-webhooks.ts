import { BaseCRUDAPI } from "../base/base-clients";
import { CreateWebhook, ReadWebhook } from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  webhooks: `${prefix}/groups/webhooks`,
  webhooksId: (id: string | number) => `${prefix}/groups/webhooks/${id}`,
  webhooksIdTest: (id: string | number) => `${prefix}/groups/webhooks/${id}/test`,
};

export class WebhooksAPI extends BaseCRUDAPI<CreateWebhook, ReadWebhook> {
  baseRoute = routes.webhooks;
  itemRoute = routes.webhooksId;
  itemTestRoute = routes.webhooksIdTest;

  async testOne(itemId: string | number) {
    return await this.requests.post<null>(`${this.itemTestRoute(itemId)}`, {});
  }
}
