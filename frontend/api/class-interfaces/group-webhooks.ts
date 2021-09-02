import { BaseCRUDAPI } from "./_base";

const prefix = "/api";

const routes = {
  webhooks: `${prefix}/groups/webhooks`,
  webhooksId: (id: string | number) => `${prefix}/groups/webhooks/${id}`,
};

export interface CreateGroupWebhook {
  enabled: boolean;
  name: string;
  url: string;
  time: string;
}

export interface GroupWebhook extends CreateGroupWebhook {
  id: string;
  groupId: string;
}

export class WebhooksAPI extends BaseCRUDAPI<GroupWebhook, CreateGroupWebhook> {
  baseRoute = routes.webhooks;
  itemRoute = routes.webhooksId;
}
