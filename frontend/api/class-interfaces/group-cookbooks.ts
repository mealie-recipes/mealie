import { BaseCRUDAPI } from "../_base";
import { Category } from "./categories";
import { CategoryBase } from "~/types/api-types/recipe";

const prefix = "/api";

export interface CreateCookBook {
  name: string;
}

export interface CookBook extends CreateCookBook {
  id: number;
  slug: string;
  description: string;
  position: number;
  group_id: number;
  categories: Category[] | CategoryBase[];
}

const routes = {
  cookbooks: `${prefix}/groups/cookbooks`,
  cookbooksId: (id: number) => `${prefix}/groups/cookbooks/${id}`,
};

export class CookbookAPI extends BaseCRUDAPI<CookBook, CreateCookBook> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: CookBook[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
