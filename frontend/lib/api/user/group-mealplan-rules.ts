import { BaseCRUDAPI } from "../base/base-clients";
import { PlanRulesCreate, PlanRulesOut } from "~/types/api-types/meal-plan";

const prefix = "/api";

const routes = {
  rule: `${prefix}/groups/mealplans/rules`,
  ruleId: (id: string | number) => `${prefix}/groups/mealplans/rules/${id}`,
};

export class MealPlanRulesApi extends BaseCRUDAPI<PlanRulesCreate, PlanRulesOut> {
  baseRoute = routes.rule;
  itemRoute = routes.ruleId;
}
