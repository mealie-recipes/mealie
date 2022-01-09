import { BaseCRUDAPI } from "../_base";
import { GroupEventNotifierCreate, GroupEventNotifierOut } from "~/types/api-types/group";

const prefix = "/api";

const routes = {
  eventNotifier: `${prefix}/groups/events/notifications`,
  eventNotifierId: (id: string | number) => `${prefix}/groups/events/notifications/${id}`,
};

export class GroupEventNotifierApi extends BaseCRUDAPI<GroupEventNotifierOut, GroupEventNotifierCreate> {
  baseRoute = routes.eventNotifier;
  itemRoute = routes.eventNotifierId;
}
