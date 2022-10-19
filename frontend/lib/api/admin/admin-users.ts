import { BaseCRUDAPI } from "../base/base-clients";
import { UnlockResults, UserIn, UserOut } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  adminUsers: `${prefix}/admin/users`,
  adminUsersId: (tag: string) => `${prefix}/admin/users/${tag}`,
  adminResetLockedUsers: (force: boolean) => `${prefix}/admin/users/unlock?force=${force ? "true" : "false"}`,
};

export class AdminUsersApi extends BaseCRUDAPI<UserIn, UserOut, UserOut> {
  baseRoute: string = routes.adminUsers;
  itemRoute = routes.adminUsersId;

  async unlockAllUsers(force = false) {
    return await this.requests.post<UnlockResults>(routes.adminResetLockedUsers(force), {});
  }
}
