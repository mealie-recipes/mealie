import { BaseCRUDAPI } from "../base/base-clients";
import { CategoryBase, GroupBase, GroupInDB, UserOut } from "~/lib/api/types/user";
import {
  CreateInviteToken,
  GroupAdminUpdate,
  GroupStatistics,
  GroupStorage,
  ReadGroupPreferences,
  ReadInviteToken,
  SetPermissions,
  UpdateGroupPreferences,
} from "~/lib/api/types/group";

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

export class GroupAPI extends BaseCRUDAPI<GroupBase, GroupInDB, GroupAdminUpdate> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await this.requests.get<GroupInDB>(routes.groupsSelf);
  }

  async getCategories() {
    return await this.requests.get<CategoryBase[]>(routes.categories);
  }

  async setCategories(payload: CategoryBase[]) {
    return await this.requests.put<CategoryBase[]>(routes.categories, payload);
  }

  async getPreferences() {
    return await this.requests.get<ReadGroupPreferences>(routes.preferences);
  }

  async setPreferences(payload: UpdateGroupPreferences) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<ReadGroupPreferences, UpdateGroupPreferences>(routes.preferences, payload);
  }

  async createInvitation(payload: CreateInviteToken) {
    return await this.requests.post<ReadInviteToken>(routes.invitation, payload);
  }

  async fetchMembers() {
    return await this.requests.get<UserOut[]>(routes.members);
  }

  async setMemberPermissions(payload: SetPermissions) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<UserOut, SetPermissions>(routes.permissions, payload);
  }

  async statistics() {
    return await this.requests.get<GroupStatistics>(routes.statistics);
  }

  async storage() {
    return await this.requests.get<GroupStorage>(routes.storage);
  }
}
