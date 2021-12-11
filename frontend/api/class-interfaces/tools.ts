import { BaseCRUDAPI } from "../_base";
import { Recipe } from "~/types/api-types/recipe";

const prefix = "/api";

export interface CreateTool {
  name: string;
  onHand: boolean;
}

export interface Tool extends CreateTool {
  id: number;
  slug: string;
}

export interface RecipeToolResponse extends Tool {
  recipes: Recipe[];
}

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
  toolsSlug: (id: string) => `${prefix}/tools/slug/${id}`,
};

export class ToolsApi extends BaseCRUDAPI<Tool, CreateTool> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;

  async byslug(slug: string) {
    return await this.requests.get<Tool>(routes.toolsSlug(slug));
  }
}
