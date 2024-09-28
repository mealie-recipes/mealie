import { BaseCRUDAPI } from "../base/base-clients";
import { PlanRulesCreate, PlanRulesOut } from "~/lib/api/types/meal-plan";

const prefix = "/api";

const routes = {
  rule: `${prefix}/households/mealplans/rules`,
  ruleId: (id: string | number) => `${prefix}/households/mealplans/rules/${id}`,
};

export class MealPlanRulesApi extends BaseCRUDAPI<PlanRulesCreate, PlanRulesOut> {
  baseRoute = routes.rule;
  itemRoute = routes.ruleId;
}
