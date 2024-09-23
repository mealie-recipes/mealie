import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { HouseholdSummary } from "~/lib/api/types/household";
import { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";

const prefix = "/api";
const exploreGroupSlug = (groupSlug: string | number) => `${prefix}/explore/groups/${groupSlug}`

const routes = {
  householdsGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/households`,
  householdsGroupSlugHouseholdSlug: (groupSlug: string | number, householdSlug: string | number) => `${exploreGroupSlug(groupSlug)}/households/${householdSlug}`,
};

export class PublicHouseholdApi extends BaseCRUDAPIReadOnly<HouseholdSummary> {
  baseRoute = routes.householdsGroupSlug(this.groupSlug);
  itemRoute = (itemId: string | number) => routes.householdsGroupSlugHouseholdSlug(this.groupSlug, itemId);

  constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
    super(requests);
  }
}
