import { BaseCRUDAPI } from "../_base";
import { GroupInDB, UserOut } from "~/types/api-types/user";
import { GroupStatistics, GroupStorage } from "~/types/api-types/group";

const prefix = "/api";

const routes = {
  groups: `${prefix}/admin/groups`,
  groupsSelf: `${prefix}/groups/self`,
  categories: `${prefix}/groups/categories`,
  members: `${prefix}/groups/members`,
  permissions: `${prefix}/groups/permissions`,

  preferences: `${prefix}/groups/preferences`,
  statistics: `${prefix}/groups/statistics`,
  storage: `${prefix}/groups/storage`,

  invitation: `${prefix}/groups/invitations`,

  groupsId: (id: string | number) => `${prefix}/admin/groups/${id}`,
};

interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface CreateGroup {
  name: string;
}

export interface UpdatePreferences {
  privateGroup: boolean;
  firstDayOfWeek: number;
  recipePublic: boolean;
  recipeShowNutrition: boolean;
  recipeShowAssets: boolean;
  recipeLandscapeView: boolean;
  recipeDisableComments: boolean;
  recipeDisableAmount: boolean;
}

export interface Preferences extends UpdatePreferences {
  id: number;
  group_id: number;
}

export interface Group extends CreateGroup {
  id: number;
  preferences: Preferences;
}

export interface CreateInvitation {
  uses: number;
}

export interface Invitation {
  group_id: number;
  token: string;
  uses_left: number;
}

export interface SetPermissions {
  userId: string;
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
}

export class GroupAPI extends BaseCRUDAPI<GroupInDB, CreateGroup> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await this.requests.get<Group>(routes.groupsSelf);
  }

  async getCategories() {
    return await this.requests.get<Category[]>(routes.categories);
  }

  async setCategories(payload: Category[]) {
    return await this.requests.put<Category[]>(routes.categories, payload);
  }

  async getPreferences() {
    return await this.requests.get<Preferences>(routes.preferences);
  }

  async setPreferences(payload: UpdatePreferences) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<Preferences, UpdatePreferences>(routes.preferences, payload);
  }

  async createInvitation(payload: CreateInvitation) {
    return await this.requests.post<Invitation>(routes.invitation, payload);
  }

  async fetchMembers() {
    return await this.requests.get<UserOut[]>(routes.members);
  }

  async setMemberPermissions(payload: SetPermissions) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<Permissions, SetPermissions>(routes.permissions, payload);
  }

  async statistics() {
    return await this.requests.get<GroupStatistics>(routes.statistics);
  }

  async storage() {
    return await this.requests.get<GroupStorage>(routes.storage);
  }
}
