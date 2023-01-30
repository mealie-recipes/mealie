import { BaseCRUDAPI } from "../base/base-clients";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";
import {
  ShoppingListCreate,
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdateBulk,
  ShoppingListOut,
  ShoppingListUpdate,
} from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
  shoppingLists: `${prefix}/groups/shopping/lists`,
  shoppingListsId: (id: string) => `${prefix}/groups/shopping/lists/${id}`,
  shoppingListIdAddRecipe: (id: string, recipeId: string) => `${prefix}/groups/shopping/lists/${id}/recipe/${recipeId}`,
  shoppingListIdRemoveRecipe: (id: string, recipeId: string) => `${prefix}/groups/shopping/lists/${id}/recipe/${recipeId}/delete`,

  shoppingListItems: `${prefix}/groups/shopping/items`,
  shoppingListItemsId: (id: string) => `${prefix}/groups/shopping/items/${id}`,
};

export class ShoppingListsApi extends BaseCRUDAPI<ShoppingListCreate, ShoppingListOut, ShoppingListUpdate> {
  baseRoute = routes.shoppingLists;
  itemRoute = routes.shoppingListsId;

  async addRecipe(itemId: string, recipeId: string, recipeIncrementQuantity = 1) {
    return await this.requests.post(routes.shoppingListIdAddRecipe(itemId, recipeId), {recipeIncrementQuantity});
  }

  async removeRecipe(itemId: string, recipeId: string, recipeDecrementQuantity = 1) {
    return await this.requests.post(routes.shoppingListIdRemoveRecipe(itemId, recipeId), {recipeDecrementQuantity});
  }
}

export class ShoppingListItemsApi extends BaseCRUDAPI<
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdateBulk
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
