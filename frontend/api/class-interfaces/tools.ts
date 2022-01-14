import { BaseCRUDAPI } from "../_base";
import { RecipeTool, RecipeToolCreate, RecipeToolResponse } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
  toolsSlug: (id: string) => `${prefix}/tools/slug/${id}`,
};

export class ToolsApi extends BaseCRUDAPI<RecipeTool, RecipeToolCreate> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;

  async byslug(slug: string) {
    return await this.requests.get<RecipeToolResponse>(routes.toolsSlug(slug));
  }
}
