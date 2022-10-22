import { BaseAPI } from "../base/base-clients";
import { SuccessResponse } from "~/lib/api/types/response";
import { SeederConfig } from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  base: `${prefix}/groups/seeders`,
  foods: `${prefix}/groups/seeders/foods`,
  units: `${prefix}/groups/seeders/units`,
  labels: `${prefix}/groups/seeders/labels`,
};

export class GroupDataSeederApi extends BaseAPI {
  foods(payload: SeederConfig) {
    return this.requests.post<SuccessResponse>(routes.foods, payload);
  }

  units(payload: SeederConfig) {
    return this.requests.post<SuccessResponse>(routes.units, payload);
  }

  labels(payload: SeederConfig) {
    return this.requests.post<SuccessResponse>(routes.labels, payload);
  }
}
