import { BaseCRUDAPI } from "../_base";
import { Category } from "./categories";
import { CategoryBase } from "~/types/api-types/recipe";

const prefix = "/api";

export interface CreateShoppingList {
  name: string;
}

export interface ShoppingList extends CreateShoppingList {
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

export class ShoppingListAPI extends BaseCRUDAPI<ShoppingList, CreateShoppingList> {
  baseRoute: string = routes.cookbooks;
  itemRoute = routes.cookbooksId;

  async updateAll(payload: ShoppingList[]) {
    return await this.requests.put(this.baseRoute, payload);
  }
}
