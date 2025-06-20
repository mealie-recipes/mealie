import { BaseCRUDAPI } from "../../base/base-clients";
import type { RecipeShareToken, RecipeShareTokenCreate } from "~/lib/api/types/recipe";

const prefix = "/api";

const routes = {
  shareToken: `${prefix}/shared/recipes`,
  shareTokenId: (id: string) => `${prefix}/shared/recipes/${id}`,
};

export class RecipeShareApi extends BaseCRUDAPI<RecipeShareTokenCreate, RecipeShareToken> {
  baseRoute: string = routes.shareToken;
  itemRoute = routes.shareTokenId;
}
