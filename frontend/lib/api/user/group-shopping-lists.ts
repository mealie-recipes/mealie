import { BaseCRUDAPI } from "../base/base-clients";
import { RecipeIngredient } from "../types/recipe";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";
import {
  ShoppingListCreate,
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdateBulk,
  ShoppingListMultiPurposeLabelUpdate,
  ShoppingListOut,
  ShoppingListUpdate,
} from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
  shoppingLists: `${prefix}/households/shopping/lists`,
  shoppingListsId: (id: string) => `${prefix}/households/shopping/lists/${id}`,
  shoppingListIdAddRecipe: (id: string, recipeId: string) => `${prefix}/households/shopping/lists/${id}/recipe/${recipeId}`,
  shoppingListIdRemoveRecipe: (id: string, recipeId: string) => `${prefix}/households/shopping/lists/${id}/recipe/${recipeId}/delete`,
  shoppingListIdUpdateLabelSettings: (id: string) => `${prefix}/households/shopping/lists/${id}/label-settings`,

  shoppingListItems: `${prefix}/households/shopping/items`,
  shoppingListItemsCreateBulk: `${prefix}/households/shopping/items/create-bulk`,
  shoppingListItemsId: (id: string) => `${prefix}/households/shopping/items/${id}`,
};

export class ShoppingListsApi extends BaseCRUDAPI<ShoppingListCreate, ShoppingListOut, ShoppingListUpdate> {
  baseRoute = routes.shoppingLists;
  itemRoute = routes.shoppingListsId;

  async addRecipe(itemId: string, recipeId: string, recipeIncrementQuantity = 1, recipeIngredients: RecipeIngredient[] | null = null) {
    return await this.requests.post(routes.shoppingListIdAddRecipe(itemId, recipeId), { recipeIncrementQuantity, recipeIngredients });
  }

  async removeRecipe(itemId: string, recipeId: string, recipeDecrementQuantity = 1) {
    return await this.requests.post(routes.shoppingListIdRemoveRecipe(itemId, recipeId), { recipeDecrementQuantity });
  }

  async updateLabelSettings(itemId: string, listSettings: ShoppingListMultiPurposeLabelUpdate[]) {
    return await this.requests.put(routes.shoppingListIdUpdateLabelSettings(itemId), listSettings);
  }
}

export class ShoppingListItemsApi extends BaseCRUDAPI<
  ShoppingListItemCreate,
  ShoppingListItemOut,
  ShoppingListItemUpdateBulk
> {
  baseRoute = routes.shoppingListItems;
  itemRoute = routes.shoppingListItemsId;

  async createMany(items: ShoppingListItemCreate[]) {
    return await this.requests.post(routes.shoppingListItemsCreateBulk, items);
  }

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
