import { BaseCRUDAPI } from "../base/base-clients";
import { CreateGroupRecipeAction, GroupRecipeActionOut } from "~/lib/api/types/household";

const prefix = "/api";

const routes = {
    groupRecipeActions: `${prefix}/households/recipe-actions`,
    groupRecipeActionsId: (id: string | number) => `${prefix}/households/recipe-actions/${id}`,
    groupRecipeActionsIdTriggerRecipeSlug: (id: string | number, recipeSlug: string, servings: number, yield_quantity: number) => `${prefix}/households/recipe-actions/${id}/trigger/${recipeSlug}/${servings}/${yield_quantity}`,
  };

  export class GroupRecipeActionsAPI extends BaseCRUDAPI<CreateGroupRecipeAction, GroupRecipeActionOut> {
    baseRoute = routes.groupRecipeActions;
    itemRoute = routes.groupRecipeActionsId;

    async triggerAction(id: string | number, recipeSlug: string, servings: number, yield_quantity: number) {
      return await this.requests.post(routes.groupRecipeActionsIdTriggerRecipeSlug(id, recipeSlug, servings, yield_quantity), {});
    }
  }
