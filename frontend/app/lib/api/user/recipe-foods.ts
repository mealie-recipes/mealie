import { BaseCRUDAPI } from "../base/base-clients";
import type { CreateIngredientFood, IngredientFood, UsdaFoodResult, UsdaNutritionData } from "~/lib/api/types/recipe";

const prefix = "/api";

const routes = {
  food: `${prefix}/foods`,
  foodsFood: (tag: string) => `${prefix}/foods/${tag}`,
  merge: `${prefix}/foods/merge`,
  usdaSearch: `${prefix}/foods/usda/search`,
  usdaNutrition: (fdcId: number) => `${prefix}/foods/usda/${fdcId}/nutrition`,
};

export class FoodAPI extends BaseCRUDAPI<CreateIngredientFood, IngredientFood> {
  baseRoute: string = routes.food;
  itemRoute = routes.foodsFood;

  merge(fromId: string, toId: string) {
    return this.requests.put<IngredientFood>(routes.merge, { fromFood: fromId, toFood: toId });
  }

  usdaSearch(query: string) {
    return this.requests.get<UsdaFoodResult[]>(routes.usdaSearch, { q: query });
  }

  usdaFetchNutrition(fdcId: number) {
    return this.requests.get<UsdaNutritionData>(routes.usdaNutrition(fdcId));
  }
}
