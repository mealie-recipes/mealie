import { BaseCRUDAPI } from "../_base";
import { CreatRandomEntry } from "~/types/api-types/meal-plan";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/groups/mealplans`,
  random: `${prefix}/groups/mealplans/random`,
  mealplanId: (id: string | number) => `${prefix}/groups/mealplans/${id}`,
};

type PlanEntryType = "breakfast" | "lunch" | "dinner" | "side";

export interface CreateMealPlan {
  date: string;
  entryType: PlanEntryType;
  title: string;
  text: string;
  recipeId?: string;
}

export interface UpdateMealPlan extends CreateMealPlan {
  id: number;
  groupId: number;
}

export interface MealPlan extends UpdateMealPlan {
  recipe: any;
}

export class MealPlanAPI extends BaseCRUDAPI<MealPlan, CreateMealPlan> {
  baseRoute = routes.mealplan;
  itemRoute = routes.mealplanId;

  async setRandom(payload: CreatRandomEntry) {
    console.log(payload);
    return await this.requests.post<MealPlan>(routes.random, payload);
  }
}
