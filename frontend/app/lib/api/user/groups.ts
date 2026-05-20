import { BaseCRUDAPI } from "../base/base-clients";
import type { PaginationData } from "../types/non-generated";
import type { QueryValue } from "../base/route";
import type { GroupBase, GroupInDB, GroupSummary, UserSummary } from "~/lib/api/types/user";
import type {
  AIProviderSettingsUpdate,
  AIProviderSettingsOut,
  GroupAdminUpdate,
  GroupStorage,
  ReadGroupPreferences,
  UpdateGroupPreferences,
} from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  groups: `${prefix}/admin/groups`,
  groupsSelf: `${prefix}/groups/self`,
  preferences: `${prefix}/groups/preferences`,
  aiProviderSettings: `${prefix}/groups/ai-providers/settings`,
  storage: `${prefix}/groups/storage`,
  members: `${prefix}/groups/members`,
  groupsId: (id: string | number) => `${prefix}/admin/groups/${id}`,
};

export class GroupAPI extends BaseCRUDAPI<GroupBase, GroupInDB, GroupAdminUpdate> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await this.requests.get<GroupSummary>(routes.groupsSelf);
  }

  async setPreferences(payload: UpdateGroupPreferences) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<ReadGroupPreferences, UpdateGroupPreferences>(routes.preferences, payload);
  }

  async setAIProviderSettings(payload: AIProviderSettingsUpdate) {
    return await this.requests.put<AIProviderSettingsOut, AIProviderSettingsUpdate>(routes.aiProviderSettings, payload);
  }

  async fetchMembers(page = 1, perPage = -1, params = {} as Record<string, QueryValue>) {
    return await this.requests.get<PaginationData<UserSummary>>(routes.members, { page, perPage, ...params });
  }

  async storage() {
    return await this.requests.get<GroupStorage>(routes.storage);
  }
}
