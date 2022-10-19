import { BaseCRUDAPI } from "../base/base-clients";
import { CreateIngredientFood, IngredientFood } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  food: `${prefix}/foods`,
  foodsFood: (tag: string) => `${prefix}/foods/${tag}`,
  merge: `${prefix}/foods/merge`,
};

export class FoodAPI extends BaseCRUDAPI<CreateIngredientFood, IngredientFood> {
  baseRoute: string = routes.food;
  itemRoute = routes.foodsFood;

  merge(fromId: string, toId: string) {
    // @ts-ignore TODO: fix this
    return this.requests.put<IngredientFood>(routes.merge, { fromFood: fromId, toFood: toId });
  }
}
