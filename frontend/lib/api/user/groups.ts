import { BaseCRUDAPI } from "../base/base-clients";
import { GroupBase, GroupInDB, GroupSummary, UserSummary } from "~/lib/api/types/user";
import { HouseholdSummary } from "~/lib/api/types/household";
import {
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
  storage: `${prefix}/groups/storage`,
  households: `${prefix}/groups/households`,
  householdsId: (id: string | number) => `${prefix}/groups/households/${id}`,
  membersHouseholdId: (householdId: string | number | null) => {
    return householdId ?
      `${prefix}/households/members?householdId=${householdId}` :
      `${prefix}/groups/members`;
  },
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

  async getPreferences() {
    return await this.requests.get<ReadGroupPreferences>(routes.preferences);
  }

  async setPreferences(payload: UpdateGroupPreferences) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<ReadGroupPreferences, UpdateGroupPreferences>(routes.preferences, payload);
  }

  async fetchMembers(householdId: string | number | null = null) {
    return await this.requests.get<UserSummary[]>(routes.membersHouseholdId(householdId));
  }

  async fetchHouseholds() {
    return await this.requests.get<HouseholdSummary[]>(routes.households);
  }

  async fetchHousehold(householdId: string | number) {
    return await this.requests.get<HouseholdSummary>(routes.householdsId(householdId));
  }

  async storage() {
    return await this.requests.get<GroupStorage>(routes.storage);
  }
}
