import { BaseAPI } from "../base/base-clients";
import { Recipe } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  recipe: (groupId: string, recipeSlug: string) => `${prefix}/explore/recipes/${groupId}/${recipeSlug}`,
};

export class ExploreApi extends BaseAPI {
  async recipe(groupId: string, recipeSlug: string) {
    return await this.requests.get<Recipe>(routes.recipe(groupId, recipeSlug));
  }
}
