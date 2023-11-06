import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { route } from "../../base";
import { Recipe } from "~/lib/api/types/recipe";
import { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";
import { RecipeSearchQuery } from "../../user/recipes/recipe";

const prefix = "/api";

const routes = {
  recipesGroupSlug: (groupSlug: string | number) => `${prefix}/explore/recipes/${groupSlug}`,
  recipesGroupSlugRecipeSlug: (groupSlug: string | number, recipeSlug: string | number) => `${prefix}/explore/recipes/${groupSlug}/${recipeSlug}`,
};

export class PublicRecipeApi extends BaseCRUDAPIReadOnly<Recipe> {
  baseRoute = routes.recipesGroupSlug(this.groupSlug);
  itemRoute = (itemId: string | number) => routes.recipesGroupSlugRecipeSlug(this.groupSlug, itemId);

  constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
    super(requests);
  }

  async search(rsq: RecipeSearchQuery) {
    return await this.requests.get<PaginationData<Recipe>>(route(routes.recipesGroupSlug(this.groupSlug), rsq));
  }
}
