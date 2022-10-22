import { BaseCRUDAPI } from "../base/base-clients";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";
import {
  ShoppingListCreate,
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdate,
  ShoppingListOut,
  ShoppingListUpdate,
} from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  shoppingLists: `${prefix}/groups/shopping/lists`,
  shoppingListsId: (id: string) => `${prefix}/groups/shopping/lists/${id}`,
  shoppingListIdAddRecipe: (id: string, recipeId: string) => `${prefix}/groups/shopping/lists/${id}/recipe/${recipeId}`,

  shoppingListItems: `${prefix}/groups/shopping/items`,
  shoppingListItemsId: (id: string) => `${prefix}/groups/shopping/items/${id}`,
};

export class ShoppingListsApi extends BaseCRUDAPI<ShoppingListCreate, ShoppingListOut, ShoppingListUpdate> {
  baseRoute = routes.shoppingLists;
  itemRoute = routes.shoppingListsId;

  async addRecipe(itemId: string, recipeId: string) {
    return await this.requests.post(routes.shoppingListIdAddRecipe(itemId, recipeId), {});
  }

  async removeRecipe(itemId: string, recipeId: string) {
    return await this.requests.delete(routes.shoppingListIdAddRecipe(itemId, recipeId));
  }
}

export class ShoppingListItemsApi extends BaseCRUDAPI<
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdate
> {
  baseRoute = routes.shoppingListItems;
  itemRoute = routes.shoppingListItemsId;

  async updateMany(items: ShoppingListItemOut[]) {
    return await this.requests.put(routes.shoppingListItems, items);
  }

  async deleteMany(items: ShoppingListItemOut[]) {
    let query = "?";

    items.forEach((item) => {
      query += `ids=${item.id}&`;
    });

    return await this.requests.delete(routes.shoppingListItems + query);
  }
}

export class ShoppingApi {
  public lists: ShoppingListsApi;
  public items: ShoppingListItemsApi;

  constructor(requests: ApiRequestInstance) {
    this.lists = new ShoppingListsApi(requests);
    this.items = new ShoppingListItemsApi(requests);
  }
}
