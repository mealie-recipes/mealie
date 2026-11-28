import { BaseCRUDAPI } from "../base/base-clients";
import type { PlanEntryCreate, RandomPlanEntryCreate, MealPlanICalTokenOut, PlanEntryOut, PlanEntryUpdate, PlanEntryReorderUpdate } from "~/lib/api/types/meal-plan";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/households/mealplans`,
  random: `${prefix}/households/mealplans/random`,
  ical: `${prefix}/households/mealplans/ical`,
  reorder: `${prefix}/households/mealplans/reorder`,
  mealplanId: (id: string | number) => `${prefix}/households/mealplans/${id}`,
};

export class MealPlanAPI extends BaseCRUDAPI<PlanEntryCreate, PlanEntryOut, PlanEntryUpdate> {
  override baseRoute = routes.mealplan;
  override itemRoute = routes.mealplanId;

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

  async reorder(payload: PlanEntryReorderUpdate[]) {
    return await this.requests.put<undefined, PlanEntryReorderUpdate[]>(routes.reorder, payload);
  }
}
