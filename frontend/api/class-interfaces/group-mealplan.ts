import { BaseCRUDAPI } from "./_base";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/groups/mealplans`,
  mealplanId: (id: string | number) => `${prefix}/groups/mealplans/${id}`,
};

type PlanEntryType = "breakfast" | "lunch" | "dinner" | "snack";

export interface CreateMealPlan {
  date: string;
  entryType: PlanEntryType;
  title: string;
  text: string;
  recipeId?: number;
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
}
