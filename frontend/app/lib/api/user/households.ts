import { BaseCRUDAPIReadOnly } from "../base/base-clients";
import type { PaginationData } from "../types/non-generated";
import type { QueryValue } from "../base/route";
import type { UserOut } from "~/lib/api/types/user";
import type {
  HouseholdOut,
  HouseholdStatistics,
  HouseholdPreferencesOut,
  SetPermissions,
  HouseholdPreferencesUpdate,
  InviteTokenCreate,
  InviteTokenOut,
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
  householdsSelfRecipesSlug: (recipeSlug: string) => `${prefix}/households/self/recipes/${recipeSlug}`,
};

export class HouseholdAPI extends BaseCRUDAPIReadOnly<HouseholdSummary> {
  baseRoute = routes.households;
  itemRoute = routes.householdsId;
  /** Returns the Household Data for the Current User
   */
  async getCurrentUserHousehold() {
    return await this.requests.get<HouseholdOut>(routes.householdsSelf);
  }

  async getCurrentUserHouseholdRecipe(recipeSlug: string) {
    return await this.requests.get<HouseholdRecipeSummary>(routes.householdsSelfRecipesSlug(recipeSlug));
  }

  async setPreferences(payload: HouseholdPreferencesUpdate) {
    // TODO: This should probably be a patch request, which isn't offered by the API currently
    return await this.requests.put<HouseholdPreferencesOut, HouseholdPreferencesUpdate>(routes.preferences, payload);
  }

  async createInvitation(payload: InviteTokenCreate) {
    return await this.requests.post<InviteTokenOut>(routes.invitation, payload);
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
