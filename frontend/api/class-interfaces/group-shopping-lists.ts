import { BaseCRUDAPI } from "../_base";
import { ApiRequestInstance } from "~/types/api";
import { RecipeIngredientFood, RecipeIngredientUnit } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  shoppingLists: `${prefix}/groups/shopping/lists`,
  shoppingListsId: (id: string) => `${prefix}/groups/shopping/lists/${id}`,
  shoppingListIdAddRecipe: (id: string, recipeId: number) => `${prefix}/groups/shopping/lists/${id}/recipe/${recipeId}`,
};

export interface ShoppingListItemCreate {
  id: string;
  shoppingListId: string;
  checked: boolean;
  position: number;
  note: string;
  quantity: number;

  isFood: boolean;
  unit: RecipeIngredientUnit | null;
  food: RecipeIngredientFood | null;

  labelId: string | null;
  label?: {
    id: string;
    name: string;
  };
}

export interface ShoppingListCreate {
  name: string;
}

export interface ShoppingListSummary extends ShoppingListCreate {
  id: string;
  groupId: string;
}

export interface ShoppingList extends ShoppingListSummary {
  listItems: ShoppingListItemCreate[];
}

export class ShoppingListsApi extends BaseCRUDAPI<ShoppingList, ShoppingListCreate> {
  baseRoute = routes.shoppingLists;
  itemRoute = routes.shoppingListsId;

  async addRecipe(itemId: string, recipeId: number) {
    return await this.requests.post(routes.shoppingListIdAddRecipe(itemId, recipeId), {});
  }
}

export class ShoppingApi {
  public lists: ShoppingListsApi;

  constructor(requests: ApiRequestInstance) {
    this.lists = new ShoppingListsApi(requests);
  }
}
