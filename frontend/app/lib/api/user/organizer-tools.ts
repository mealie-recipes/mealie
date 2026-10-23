import { BaseCRUDAPI } from "../base/base-clients";
import { config } from "../config";
import type { RecipeTool, RecipeToolCreate, RecipeToolResponse } from "~/lib/api/types/recipe";

const prefix = config.PREFIX + "/organizers";

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
  toolsSlug: (id: string) => `${prefix}/tools/slug/${id}`,
  toolsEmpty: `${prefix}/tools/empty`,
  toolsMerge: `${prefix}/tools/merge`,
};

export class ToolsApi extends BaseCRUDAPI<RecipeToolCreate, RecipeTool> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeToolResponse>(routes.toolsSlug(slug));
  }

  async getEmpty() {
    return await this.requests.get<RecipeTool[]>(routes.toolsEmpty);
  }

  merge(fromId: string, toId: string) {
    return this.requests.post<RecipeTool>(routes.toolsMerge, { fromId, toId });
  }
}
