import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import type { TagCreate, TagOut, TagWithRecipes } from "~/lib/api/types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tags: `${prefix}/tags`,
  tagsId: (tag: string) => `${prefix}/tags/${tag}`,
  tagsSlug: (tag: string) => `${prefix}/tags/slug/${tag}`,
  tagsEmpty: `${prefix}/tags/empty`,
  tagsMerge: `${prefix}/tags/merge`,
};

/** Reading or updating one tag responds with its recipes too; the list, create and merge routes do not. */
export class TagsAPI extends BaseCRUDAPI<TagCreate, TagWithRecipes, TagCreate, TagOut, TagOut> {
  baseRoute: string = routes.tags;
  itemRoute = routes.tagsId;

  async bySlug(slug: string) {
    return await this.requests.get<TagWithRecipes>(routes.tagsSlug(slug));
  }

  async getEmpty() {
    return await this.requests.get<TagOut[]>(routes.tagsEmpty);
  }

  merge(fromId: string, toId: string) {
    return this.requests.post<TagOut>(routes.tagsMerge, { fromId, toId });
  }
}
