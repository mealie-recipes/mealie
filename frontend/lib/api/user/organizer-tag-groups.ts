import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import type { TagGroupIn, TagGroupOut, TagGroupSummary } from "~/lib/api/types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tagGroups: `${prefix}/tag-groups`,
  tagGroupsId: (id: string) => `${prefix}/tag-groups/${id}`,
  tagGroupsSlug: (slug: string) => `${prefix}/tag-groups/slug/${slug}`,
};

export class TagGroupsAPI extends BaseCRUDAPI<TagGroupIn, TagGroupOut> {
  baseRoute: string = routes.tagGroups;
  itemRoute = routes.tagGroupsId;

  async bySlug(slug: string) {
    return await this.requests.get<TagGroupSummary>(routes.tagGroupsSlug(slug));
  }
}
