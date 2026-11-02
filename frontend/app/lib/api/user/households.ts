import { BaseCRUDAPIReadOnly } from "../base/base-clients";
import type { PaginationData } from "../types/non-generated";
import type { QueryValue } from "../base/route";
import type { UserOut } from "~/lib/api/types/user";
import type { SuccessResponse } from "~/lib/api/types/response";
import type {
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
  householdsSelfFoodsOnHand: `${prefix}/households/self/foods-on-hand`,
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
    return await this.requests.get<HouseholdInDB>(routes.householdsSelf);
  }

  async getCurrentUserHouseholdRecipe(recipeSlug: string) {
    return await this.requests.get<HouseholdRecipeSummary>(routes.householdsSelfRecipesSlug(recipeSlug));
  }

  /** Marks foods as on hand for the current user's household
   */
  async addFoodsOnHand(foodIds: string[]) {
    // callers show their own, more specific confirmation instead of the API's generic message
    return await this.requests.post<SuccessResponse>(
      routes.householdsSelfFoodsOnHand,
      foodIds,
      { suppressAlert: true },
    );
  }

  /** Removes foods from the current user's household's on hand foods
   */
  async removeFoodsOnHand(foodIds: string[]) {
    const query = new URLSearchParams(foodIds.map(id => ["ids", id])).toString();
    // callers show their own, more specific confirmation instead of the API's generic message
    return await this.requests.delete<SuccessResponse>(
      `${routes.householdsSelfFoodsOnHand}?${query}`,
      { suppressAlert: true },
    );
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
