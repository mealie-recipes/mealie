import { BaseAPI } from "../base/base-clients";
import { Recipe } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  recipeShareToken: (token: string) => `${prefix}/recipes/shared/${token}`,
};

export class SharedApi extends BaseAPI {
  async getShared(item_id: string) {
    return await this.requests.get<Recipe>(routes.recipeShareToken(item_id));
  }
}
