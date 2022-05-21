import { BaseCRUDAPI } from "../_base";
import { UserIn, UserOut } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  adminUsers: `${prefix}/admin/users`,
  adminUsersId: (tag: string) => `${prefix}/admin/users/${tag}`,
};

export class AdminUsersApi extends BaseCRUDAPI<UserIn, UserOut, UserOut> {
  baseRoute: string = routes.adminUsers;
  itemRoute = routes.adminUsersId;
}
