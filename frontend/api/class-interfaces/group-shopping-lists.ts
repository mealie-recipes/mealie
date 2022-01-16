import { BaseCRUDAPI } from "../_base";
import { ApiRequestInstance } from "~/types/api";
import {
  ShoppingListCreate,
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListOut,
} from "~/types/api-types/group";

const prefix = "/api";

const routes = {
  shoppingLists: `${prefix}/groups/shopping/lists`,
  shoppingListsId: (id: string) => `${prefix}/groups/shopping/lists/${id}`,
  shoppingListIdAddRecipe: (id: string, recipeId: number) => `${prefix}/groups/shopping/lists/${id}/recipe/${recipeId}`,

  shoppingListItems: `${prefix}/groups/shopping/items`,
  shoppingListItemsId: (id: string) => `${prefix}/groups/shopping/items/${id}`,
};

export class ShoppingListsApi extends BaseCRUDAPI<ShoppingListOut, ShoppingListCreate> {
  baseRoute = routes.shoppingLists;
  itemRoute = routes.shoppingListsId;

  async addRecipe(itemId: string, recipeId: number) {
    return await this.requests.post(routes.shoppingListIdAddRecipe(itemId, recipeId), {});
  }

  async removeRecipe(itemId: string, recipeId: number) {
    return await this.requests.delete(routes.shoppingListIdAddRecipe(itemId, recipeId));
  }
}

export class ShoppingListItemsApi extends BaseCRUDAPI<ShoppingListItemOut, ShoppingListItemCreate> {
  baseRoute = routes.shoppingListItems;
  itemRoute = routes.shoppingListItemsId;
}

export class ShoppingApi {
  public lists: ShoppingListsApi;
  public items: ShoppingListItemsApi;

  constructor(requests: ApiRequestInstance) {
    this.lists = new ShoppingListsApi(requests);
    this.items = new ShoppingListItemsApi(requests);
  }
}
