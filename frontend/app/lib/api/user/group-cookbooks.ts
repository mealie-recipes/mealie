import { BaseCRUDAPI } from "../base/base-clients";
import type { CookBookCreate, CookBookOut, CookBookUpdate } from "~/lib/api/types/cookbook";

const prefix = "/api";

const routes = {
  cookbooks: `${prefix}/households/cookbooks`,
  cookbooksId: (id: number) => `${prefix}/households/cookbooks/${id}`,
};

export class CookbookAPI extends BaseCRUDAPI<CookBookCreate, CookBookOut, CookBookUpdate> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: CookBookUpdate[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
