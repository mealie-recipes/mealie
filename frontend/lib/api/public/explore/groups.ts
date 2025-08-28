import { BaseAPI } from "~/lib/api/base/base-clients";
import { ReadGroupPreferences } from "~/lib/api/types/group";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

const prefix = "/api";
const exploreGroupSlug = (groupSlug: string | number) => `${prefix}/explore/groups/${groupSlug}`

export class PublicGroupApi extends BaseAPI {
  constructor(requests: ApiRequestInstance, groupSlug: string) {
    super(requests);
  }

  async getPreferences(groupSlug: string) {
    return await this.requests.get<ReadGroupPreferences>(`${exploreGroupSlug(groupSlug)}/preferences`);
  }
}
