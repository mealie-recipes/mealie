import { BaseCRUDAPI } from "../_base";
import { RecipeTagResponse, TagIn } from "~/types/api-types/recipe";
import { config } from "~/api/config";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tags: `${prefix}/tags`,
  tagsId: (tag: string) => `${prefix}/tags/${tag}`,
  tagsSlug: (tag: string) => `${prefix}/tags/slug/${tag}`,
};

export class TagsAPI extends BaseCRUDAPI<RecipeTagResponse, TagIn> {
  baseRoute: string = routes.tags;
  itemRoute = routes.tagsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeTagResponse>(routes.tagsSlug(slug));
  }
}
