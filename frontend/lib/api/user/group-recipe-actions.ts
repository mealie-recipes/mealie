import { BaseCRUDAPI } from "../base/base-clients";
import { CreateGroupRecipeAction, GroupRecipeActionOut } from "~/lib/api/types/group";

const prefix = "/api";

const routes = {
    groupRecipeActions: `${prefix}/groups/recipe-actions`,
    groupRecipeActionsId: (id: string | number) => `${prefix}/groups/recipe-actions/${id}`,
  };

  export class GroupRecipeActionsAPI extends BaseCRUDAPI<CreateGroupRecipeAction, GroupRecipeActionOut> {
    baseRoute = routes.groupRecipeActions;
    itemRoute = routes.groupRecipeActionsId;
  }
