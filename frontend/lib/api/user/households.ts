import { BaseCRUDAPI } from "../base/base-clients";
import { UserOut } from "~/lib/api/types/user";
import {
  HouseholdCreate,
  HouseholdInDB,
  UpdateHouseholdAdmin,
  HouseholdStatistics,
  ReadHouseholdPreferences,
  SetPermissions,
  UpdateHouseholdPreferences,
  CreateInviteToken,
  ReadInviteToken,
} from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  households: `${prefix}/admin/households`,
  householdsSelf: `${prefix}/households/self`,
  members: `${prefix}/households/members`,
  permissions: `${prefix}/households/permissions`,

  preferences: `${prefix}/households/preferences`,
  statistics: `${prefix}/households/statistics`,
  invitation: `${prefix}/households/invitations`,

  householdsId: (id: string | number) => `${prefix}/admin/households/${id}`,
};

export class HouseholdAPI extends BaseCRUDAPI<HouseholdCreate, HouseholdInDB, UpdateHouseholdAdmin> {
  baseRoute = routes.households;
  itemRoute = routes.householdsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserHousehold() {
    return await this.requests.get<HouseholdInDB>(routes.householdsSelf);
  }

  async getPreferences() {
    return await this.requests.get<ReadHouseholdPreferences>(routes.preferences);
  }

  async setPreferences(payload: UpdateHouseholdPreferences) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<ReadHouseholdPreferences, UpdateHouseholdPreferences>(routes.preferences, payload);
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
    return await this.requests.get<HouseholdStatistics>(routes.statistics);
  }
}
