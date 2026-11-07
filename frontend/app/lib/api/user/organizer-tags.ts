import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import type { RecipeTagResponse, TagIn, TagOut } from "~/lib/api/types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tags: `${prefix}/tags`,
  tagsId: (tag: string) => `${prefix}/tags/${tag}`,
  tagsSlug: (tag: string) => `${prefix}/tags/slug/${tag}`,
  tagsEmpty: `${prefix}/tags/empty`,
  tagsMerge: `${prefix}/tags/merge`,
  tagsRemoveFromRecipes: (tag: string) => `${prefix}/tags/${tag}/remove-from-recipes`,
};

export class TagsAPI extends BaseCRUDAPI<TagIn, RecipeTagResponse> {
  baseRoute: string = routes.tags;
  itemRoute = routes.tagsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeTagResponse>(routes.tagsSlug(slug));
  }

  async getEmpty() {
    return await this.requests.get<RecipeTagResponse[]>(routes.tagsEmpty);
  }

  merge(fromId: string, toId: string) {
    return this.requests.post<RecipeTagResponse>(routes.tagsMerge, { fromId, toId });
  }

  removeFromRecipes(tagId: string, recipeIds: string[]) {
    return this.requests.post<TagOut>(routes.tagsRemoveFromRecipes(tagId), { recipeIds });
  }
}
