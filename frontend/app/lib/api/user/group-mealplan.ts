import { BaseCRUDAPI } from "../base/base-clients";
import type {
  CreatePlanEntry,
  CreateRandomEntry,
  ReadMealPlanICalToken,
  ReadPlanEntry,
  ReorderPlanEntriesByDay,
  UpdatePlanEntry,
} from "~/lib/api/types/meal-plan";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/households/mealplans`,
  random: `${prefix}/households/mealplans/random`,
  ical: `${prefix}/households/mealplans/ical`,
  reorder: `${prefix}/households/mealplans/reorder`,
  mealplanId: (id: string | number) => `${prefix}/households/mealplans/${id}`,
};

export class MealPlanAPI extends BaseCRUDAPI<CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry> {
  override baseRoute = routes.mealplan;
  override itemRoute = routes.mealplanId;

  async setRandom(payload: CreateRandomEntry) {
    return await this.requests.post<ReadPlanEntry>(routes.random, payload);
  }

  async getICalToken() {
    return await this.requests.get<ReadMealPlanICalToken>(routes.ical);
  }

  async createICalToken() {
    return await this.requests.post<ReadMealPlanICalToken>(routes.ical, {});
  }

  async deleteICalToken() {
    return await this.requests.delete<ReadMealPlanICalToken>(routes.ical);
  }

  async reorder(payload: ReorderPlanEntriesByDay[]) {
    return await this.requests.put<undefined, ReorderPlanEntriesByDay[]>(routes.reorder, payload);
  }
}
