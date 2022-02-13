import { BaseCRUDAPI } from "../_base";
import { CategoryBase } from "~/types/api-types/recipe";
import { RecipeCategory } from "~/types/api-types/user";

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
  categories: RecipeCategory[] | CategoryBase[];
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
