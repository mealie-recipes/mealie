import { BaseCRUDAPI } from "../_base";
import { RecipeTool, RecipeToolCreate, RecipeToolResponse } from "~/types/api-types/recipe";

import { config } from "~/api/config";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
  toolsSlug: (id: string) => `${prefix}/tools/slug/${id}`,
};

export class ToolsApi extends BaseCRUDAPI<RecipeTool, RecipeToolCreate> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeToolResponse>(routes.toolsSlug(slug));
  }
}
