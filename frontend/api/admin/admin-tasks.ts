import { BaseAPI } from "../_base";
import { ServerTask } from "~/types/api-types/server";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/server-tasks`,
};

export class AdminTaskAPI extends BaseAPI {
  async testTask() {
    return await this.requests.post<ServerTask>(`${routes.base}`, {});
  }

  async getAll() {
    return await this.requests.get<ServerTask[]>(routes.base);
  }
}
