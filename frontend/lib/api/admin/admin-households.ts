import { BaseCRUDAPI } from "../base/base-clients";
import { HouseholdCreate, HouseholdInDB, UpdateHouseholdAdmin } from "~/lib/api/types/household";
const prefix = "/api";

const routes = {
  adminHouseholds: `${prefix}/admin/households`,
  adminHouseholdsId: (id: string) => `${prefix}/admin/households/${id}`,
};

export class AdminHouseholdsApi extends BaseCRUDAPI<HouseholdCreate, HouseholdInDB, UpdateHouseholdAdmin> {
  baseRoute: string = routes.adminHouseholds;
  itemRoute = routes.adminHouseholdsId;
}
