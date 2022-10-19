import { BaseCRUDAPI } from "../base/base-clients";
import { CreateWebhook, ReadWebhook } from "~/types/api-types/group";

const prefix = "/api";

const routes = {
  webhooks: `${prefix}/groups/webhooks`,
  webhooksId: (id: string | number) => `${prefix}/groups/webhooks/${id}`,
};

export class WebhooksAPI extends BaseCRUDAPI<CreateWebhook, ReadWebhook> {
  baseRoute = routes.webhooks;
  itemRoute = routes.webhooksId;
}
