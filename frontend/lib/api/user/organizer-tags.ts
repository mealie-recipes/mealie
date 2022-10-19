import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import { RecipeTagResponse, TagIn } from "~/types/api-types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tags: `${prefix}/tags`,
  tagsId: (tag: string) => `${prefix}/tags/${tag}`,
  tagsSlug: (tag: string) => `${prefix}/tags/slug/${tag}`,
};

export class TagsAPI extends BaseCRUDAPI<TagIn, RecipeTagResponse> {
  baseRoute: string = routes.tags;
  itemRoute = routes.tagsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeTagResponse>(routes.tagsSlug(slug));
  }
}
