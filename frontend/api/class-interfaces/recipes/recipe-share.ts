import { BaseCRUDAPI } from "~/api/_base";

const prefix = "/api";

const routes = {
  shareToken: `${prefix}/shared/recipes`,
  shareTokenId: (id: string) => `${prefix}/shared/recipes/${id}`,
};

export interface RecipeShareTokenCreate {
  recipeId: string;
  expiresAt?: Date;
}

export interface RecipeShareToken {
  recipeId: string;
  id: string;
  groupId: number;
  expiresAt: string;
  createdAt: string;
}

export class RecipeShareApi extends BaseCRUDAPI<RecipeShareToken, RecipeShareTokenCreate> {
  baseRoute: string = routes.shareToken;
  itemRoute = routes.shareTokenId;
}
