import { BaseCRUDAPI } from "../base/base-clients";
import type { HouseholdCreate, HouseholdOut, HouseholdAdminUpdate } from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  adminHouseholds: `${prefix}/admin/households`,
  adminHouseholdsId: (id: string) => `${prefix}/admin/households/${id}`,
};

export class AdminHouseholdsApi extends BaseCRUDAPI<HouseholdCreate, HouseholdOut, HouseholdAdminUpdate> {
  baseRoute: string = routes.adminHouseholds;
  itemRoute = routes.adminHouseholdsId;
}
