import { BaseCRUDAPI } from "../_base";

const prefix = "/api";

export interface CreateFood {
  name: string;
  description: string;
}

export interface Food extends CreateFood {
  id: number;
}

const routes = {
  food: `${prefix}/foods`,
  foodsFood: (tag: string) => `${prefix}/foods/${tag}`,
};

export class FoodAPI extends BaseCRUDAPI<Food, CreateFood> {
  baseRoute: string = routes.food;
  itemRoute = routes.foodsFood;
}
