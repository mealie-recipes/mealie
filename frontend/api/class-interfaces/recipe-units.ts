import { BaseCRUDAPI } from "../_base";
import { CreateIngredientUnit, IngredientUnit } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  unit: `${prefix}/units`,
  unitsUnit: (tag: string) => `${prefix}/units/${tag}`,
};

export class UnitAPI extends BaseCRUDAPI<IngredientUnit, CreateIngredientUnit> {
  baseRoute: string = routes.unit;
  itemRoute = routes.unitsUnit;
}
