import { BaseCRUDAPI } from "../_base";
import { CreateIngredientFood, IngredientFood } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  food: `${prefix}/foods`,
  foodsFood: (tag: string) => `${prefix}/foods/${tag}`,
};

export class FoodAPI extends BaseCRUDAPI<IngredientFood, CreateIngredientFood> {
  baseRoute: string = routes.food;
  itemRoute = routes.foodsFood;
}
