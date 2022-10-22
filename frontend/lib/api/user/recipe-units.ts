import { BaseCRUDAPI } from "../base/base-clients";
import { CreateIngredientUnit, IngredientUnit } from "~/lib/api/types/recipe";

const prefix = "/api";

const routes = {
  unit: `${prefix}/units`,
  unitsUnit: (tag: string) => `${prefix}/units/${tag}`,
  merge: `${prefix}/units/merge`,
};

export class UnitAPI extends BaseCRUDAPI<CreateIngredientUnit, IngredientUnit> {
  baseRoute: string = routes.unit;
  itemRoute = routes.unitsUnit;

  merge(fromId: string, toId: string) {
    // @ts-ignore TODO: fix this
    return this.requests.put<IngredientUnit>(routes.merge, { fromUnit: fromId, toUnit: toId });
  }
}
