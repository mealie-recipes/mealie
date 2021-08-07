import { requests } from "../requests";
import { BaseCRUDAPI } from "./_base";
import { GroupInDB } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  groups: `${prefix}/groups`,
  groupsSelf: `${prefix}/groups/self`,

  groupsId: (id: string | number) => `${prefix}/groups/${id}`,
};

export interface CreateGroup {
  name: string;
}

export class GroupAPI extends BaseCRUDAPI<GroupInDB, CreateGroup> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await requests.get(routes.groupsSelf);
  }
}
