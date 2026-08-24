import { BaseCRUDAPI } from "../base/base-clients";
import type { GroupBase, GroupInDB } from "~/lib/api/types/user";
import type { GroupAdminUpdate } from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  adminUsers: `${prefix}/admin/groups`,
  adminUsersId: (id: string) => `${prefix}/admin/groups/${id}`,
};

export class AdminGroupsApi extends BaseCRUDAPI<GroupBase, GroupInDB, GroupAdminUpdate> {
  baseRoute: string = routes.adminUsers;
  itemRoute = routes.adminUsersId;
}
