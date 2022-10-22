import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import { RecipeTool, RecipeToolCreate, RecipeToolResponse } from "~/lib/api/types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
  toolsSlug: (id: string) => `${prefix}/tools/slug/${id}`,
};

export class ToolsApi extends BaseCRUDAPI<RecipeToolCreate, RecipeTool> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeToolResponse>(routes.toolsSlug(slug));
  }
}
