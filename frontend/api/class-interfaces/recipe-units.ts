import { BaseCRUDAPI } from "../_base";
import { CreateIngredientUnit, IngredientUnit } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  unit: `${prefix}/units`,
  unitsUnit: (tag: string) => `${prefix}/units/${tag}`,
  merge: `${prefix}/units/merge`,
};

export class UnitAPI extends BaseCRUDAPI<IngredientUnit, CreateIngredientUnit> {
  baseRoute: string = routes.unit;
  itemRoute = routes.unitsUnit;

  merge(fromId: string, toId: string) {
    // @ts-ignore TODO: fix this
    return this.requests.put<IngredientUnit>(routes.merge, { fromUnit: fromId, toUnit: toId });
  }
}
