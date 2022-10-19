import { BaseCRUDAPI } from "../base/base-clients";
import { CreateCookBook, RecipeCookBook, UpdateCookBook } from "~/types/api-types/cookbook";

const prefix = "/api";

const routes = {
  cookbooks: `${prefix}/groups/cookbooks`,
  cookbooksId: (id: number) => `${prefix}/groups/cookbooks/${id}`,
};

export class CookbookAPI extends BaseCRUDAPI<CreateCookBook, RecipeCookBook, UpdateCookBook> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: UpdateCookBook[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
