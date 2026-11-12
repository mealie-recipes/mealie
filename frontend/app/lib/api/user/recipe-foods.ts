import { BaseCRUDAPI } from "../base/base-clients";
import type { IngredientFoodCreate, IngredientFoodOut } from "~/lib/api/types/recipe";

const prefix = "/api";

const routes = {
  food: `${prefix}/foods`,
  foodsFood: (tag: string) => `${prefix}/foods/${tag}`,
  foodsEmpty: `${prefix}/foods/empty`,
  merge: `${prefix}/foods/merge`,
};

export class FoodAPI extends BaseCRUDAPI<IngredientFoodCreate, IngredientFoodOut> {
  baseRoute: string = routes.food;
  itemRoute = routes.foodsFood;

  async getEmpty() {
    return await this.requests.get<IngredientFoodOut[]>(routes.foodsEmpty);
  }

  merge(fromId: string, toId: string) {
    return this.requests.put<IngredientFoodOut>(routes.merge, { fromFood: fromId, toFood: toId });
  }
}
