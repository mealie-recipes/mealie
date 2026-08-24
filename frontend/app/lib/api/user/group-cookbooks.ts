import { BaseCRUDAPI } from "../base/base-clients";
import type { CreateCookBook, ReadCookBook, UpdateCookBook } from "~/lib/api/types/cookbook";

const prefix = "/api";

const routes = {
  cookbooks: `${prefix}/households/cookbooks`,
  cookbooksId: (id: number) => `${prefix}/households/cookbooks/${id}`,
};

export class CookbookAPI extends BaseCRUDAPI<CreateCookBook, ReadCookBook, UpdateCookBook> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: UpdateCookBook[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
