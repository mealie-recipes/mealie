import { BaseCRUDAPI } from "~/api/_base";
import { RecipeShareToken, RecipeShareTokenCreate } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  shareToken: `${prefix}/shared/recipes`,
  shareTokenId: (id: string) => `${prefix}/shared/recipes/${id}`,
};

export class RecipeShareApi extends BaseCRUDAPI<RecipeShareTokenCreate, RecipeShareToken> {
  baseRoute: string = routes.shareToken;
  itemRoute = routes.shareTokenId;
}
