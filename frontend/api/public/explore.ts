import { BaseAPI } from "../_base";
import { Recipe, RecipeSummary } from "~/types/api-types/recipe";
import { PaginationData } from "~/types/api";

const prefix = "/api";

const routes = {
  recipe: (groupId: string, recipeSlug: string) => `${prefix}/explore/recipes/${groupId}/${recipeSlug}`,
  recipes: (groupId: string) => `${prefix}/explore/recipes/${groupId}`,
};

export class ExploreApi extends BaseAPI {
  async recipe(groupId: string, recipeSlug: string) {
    return await this.requests.get<Recipe>(routes.recipe(groupId, recipeSlug));
  }

  async allRecipes(groupId: string) {
    return await this.requests.get<PaginationData<RecipeSummary>>(routes.recipes(groupId));
  }
}
