import { BaseCRUDAPIReadOnly } from "../base/base-clients";
import { PaginationData } from "../types/non-generated";
import { QueryValue } from "../base/route";
import { UserOut } from "~/lib/api/types/user";
import {
  HouseholdInDB,
  HouseholdStatistics,
  ReadHouseholdPreferences,
  SetPermissions,
  UpdateHouseholdPreferences,
  CreateInviteToken,
  ReadInviteToken,
  HouseholdSummary,
  HouseholdRecipeSummary,
} from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  households: `${prefix}/groups/households`,
  householdsSelf: `${prefix}/households/self`,
  members: `${prefix}/households/members`,
  permissions: `${prefix}/households/permissions`,

  preferences: `${prefix}/households/preferences`,
  statistics: `${prefix}/households/statistics`,
  invitation: `${prefix}/households/invitations`,

  householdsId: (id: string | number) => `${prefix}/groups/households/${id}`,
  householdsSelfRecipesSlug: (recipeSlug: string) =>  `${prefix}/households/self/recipes/${recipeSlug}`,
};

export class HouseholdAPI extends BaseCRUDAPIReadOnly<HouseholdSummary> {
  baseRoute = routes.households;
  itemRoute = routes.householdsId;
  /** Returns the Household Data for the Current User
   */
  async getCurrentUserHousehold() {
    return await this.requests.get<HouseholdInDB>(routes.householdsSelf);
  }

  async getCurrentUserHouseholdRecipe(recipeSlug: string) {
    return await this.requests.get<HouseholdRecipeSummary>(routes.householdsSelfRecipesSlug(recipeSlug));
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

  async fetchMembers(page = 1, perPage = -1, params = {} as Record<string, QueryValue>) {
    return await this.requests.get<PaginationData<UserOut>>(routes.members, { page, perPage, ...params });
  }

  async setMemberPermissions(payload: SetPermissions) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<UserOut, SetPermissions>(routes.permissions, payload);
  }

  async statistics() {
    return await this.requests.get<HouseholdStatistics>(routes.statistics);
  }
}
