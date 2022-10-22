import { BaseCRUDAPI } from "../base/base-clients";
import { CreatePlanEntry, CreateRandomEntry, ReadPlanEntry, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

const prefix = "/api";

const routes = {
  mealplan: `${prefix}/groups/mealplans`,
  random: `${prefix}/groups/mealplans/random`,
  mealplanId: (id: string | number) => `${prefix}/groups/mealplans/${id}`,
};

export class MealPlanAPI extends BaseCRUDAPI<CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry> {
  baseRoute = routes.mealplan;
  itemRoute = routes.mealplanId;

  async setRandom(payload: CreateRandomEntry) {
    console.log(payload);
    return await this.requests.post<ReadPlanEntry>(routes.random, payload);
  }
}
