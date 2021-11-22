import { BaseCRUDAPI } from "../_base";

const prefix = "/api";

export interface CreateTool {
  name: string;
}

export interface Tool extends CreateTool {
  id: number;
}

const routes = {
  tools: `${prefix}/tools`,
  toolsId: (id: string) => `${prefix}/tools/${id}`,
};

export class ToolsApi extends BaseCRUDAPI<Tool, CreateTool> {
  baseRoute: string = routes.tools;
  itemRoute = routes.toolsId;
}
