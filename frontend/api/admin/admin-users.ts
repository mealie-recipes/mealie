import { BaseCRUDAPI } from "../_base";

const prefix = "/api";

interface UserCreate {
  username: string;
  fullName: string;
  email: string;
  admin: boolean;
  group: string;
  advanced: boolean;
  canInvite: boolean;
  canManage: boolean;
  canOrganize: boolean;
  password: string;
}

export interface UserToken {
  name: string;
  id: number;
  createdAt: Date;
}

interface UserRead extends UserToken {
  id: number;
  groupId: number;
  favoriteRecipes: any[];
  tokens: UserToken[];
}

const routes = {
  adminUsers: `${prefix}/admin/users`,
  adminUsersId: (tag: string) => `${prefix}/admin/users/${tag}`,
};

export class AdminUsersApi extends BaseCRUDAPI<UserRead, UserCreate> {
  baseRoute: string = routes.adminUsers;
  itemRoute = routes.adminUsersId;
}
