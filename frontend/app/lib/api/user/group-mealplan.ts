import { BaseCRUDAPI } from "../base/base-clients";
import type { PlanEntryCreate, RandomPlanEntryCreate, MealPlanICalTokenOut, PlanEntryOut, PlanEntryUpdate } from "~/lib/api/types/meal-plan";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/households/mealplans`,
  random: `${prefix}/households/mealplans/random`,
  ical: `${prefix}/households/mealplans/ical`,
  mealplanId: (id: string | number) => `${prefix}/households/mealplans/${id}`,
};

export class MealPlanAPI extends BaseCRUDAPI<PlanEntryCreate, PlanEntryOut, PlanEntryUpdate> {
  baseRoute = routes.mealplan;
  itemRoute = routes.mealplanId;

  async setRandom(payload: RandomPlanEntryCreate) {
    return await this.requests.post<PlanEntryOut>(routes.random, payload);
  }

  async getICalToken() {
    return await this.requests.get<MealPlanICalTokenOut>(routes.ical);
  }

  async createICalToken() {
    return await this.requests.post<MealPlanICalTokenOut>(routes.ical, {});
  }

  async deleteICalToken() {
    return await this.requests.delete<MealPlanICalTokenOut>(routes.ical);
  }
}
