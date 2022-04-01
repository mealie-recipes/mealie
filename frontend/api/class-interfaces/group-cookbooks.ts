import { BaseCRUDAPI } from "../_base";
import { CreateCookBook, RecipeCookBook, UpdateCookBook } from "~/types/api-types/cookbook";

const prefix = "/api";

const routes = {
  cookbooks: `${prefix}/groups/cookbooks`,
  cookbooksId: (id: number) => `${prefix}/groups/cookbooks/${id}`,
};

export class CookbookAPI extends BaseCRUDAPI<RecipeCookBook, CreateCookBook> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: UpdateCookBook[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
