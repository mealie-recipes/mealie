import { BaseAPI } from "../_base";
import { ServerTask } from "~/types/api-types/server";
const prefix = "/api";

const routes = {
  base: `${prefix}/groups/server-tasks`,
};

export class GroupServerTaskAPI extends BaseAPI {
  async getAll() {
    return await this.requests.get<ServerTask[]>(routes.base);
  }
}
