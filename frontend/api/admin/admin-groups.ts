import { BaseCRUDAPI } from "../_base";
import { UserRead } from "./admin-users";
const prefix = "/api";

export interface Token {
  name: string;
  id: number;
  createdAt: Date;
}

export interface Preferences {
  privateGroup: boolean;
  firstDayOfWeek: number;
  recipePublic: boolean;
  recipeShowNutrition: boolean;
  recipeShowAssets: boolean;
  recipeLandscapeView: boolean;
  recipeDisableComments: boolean;
  recipeDisableAmount: boolean;
  groupId: number;
  id: number;
}

export interface GroupCreate {
  name: string;
}

export interface GroupRead extends GroupCreate {
  id: number;
  categories: any[];
  webhooks: any[];
  users: UserRead[];
  preferences: Preferences;
}

export interface AdminGroupUpdate {
  name: string;
  id: number;
  preferences: Preferences;
}

const routes = {
  adminUsers: `${prefix}/admin/groups`,
  adminUsersId: (id: number) => `${prefix}/admin/groups/${id}`,
};

export class AdminGroupsApi extends BaseCRUDAPI<GroupRead, GroupCreate> {
  baseRoute: string = routes.adminUsers;
  itemRoute = routes.adminUsersId;

  async updateOne(id: number, payload: AdminGroupUpdate) {
    return await this.requests.put<GroupRead>(this.itemRoute(id), payload);
  }
}
