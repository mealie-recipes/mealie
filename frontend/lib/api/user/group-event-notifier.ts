import { BaseCRUDAPI } from "../base/base-clients";
import { GroupEventNotifierCreate, GroupEventNotifierOut, GroupEventNotifierUpdate } from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  eventNotifier: `${prefix}/households/events/notifications`,
  eventNotifierId: (id: string | number) => `${prefix}/households/events/notifications/${id}`,
};

export class GroupEventNotifierApi extends BaseCRUDAPI<
  GroupEventNotifierCreate,
  GroupEventNotifierOut,
  GroupEventNotifierUpdate
> {
  baseRoute = routes.eventNotifier;
  itemRoute = routes.eventNotifierId;

  async test(itemId: string) {
    return await this.requests.post(`${this.baseRoute}/${itemId}/test`, {});
  }
}
