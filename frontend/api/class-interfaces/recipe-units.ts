import { BaseCRUDAPI } from "./_base";

const prefix = "/api";

export interface CreateUnit {
  name: string;
  abbreviation: string;
  description: string;
}

export interface Unit extends CreateUnit {
  id: number;
}

const routes = {
  unit: `${prefix}/units`,
  unitsUnit: (tag: string) => `${prefix}/units/${tag}`,
};

export class UnitAPI extends BaseCRUDAPI<Unit, CreateUnit> {
  baseRoute: string = routes.unit;
  itemRoute = routes.unitsUnit;
}
