import { BaseAPI } from "../base/base-clients";
import { Recipe } from "~/lib/api/types/recipe";

const prefix = "/api";

const routes = {
  recipe: (groupSlug: string, recipeSlug: string) => `${prefix}/explore/recipes/${groupSlug}/${recipeSlug}`,
};

export class ExploreApi extends BaseAPI {
  async recipe(groupSlug: string, recipeSlug: string) {
    return await this.requests.get<Recipe>(routes.recipe(groupSlug, recipeSlug));
  }
}
