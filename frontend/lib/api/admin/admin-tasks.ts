import { BaseAPI } from "../base/base-clients";
import { ServerTask } from "~/lib/api/types/server";
import { PaginationData } from "~/lib/api/types/non-generated";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/server-tasks`,
};

export class AdminTaskAPI extends BaseAPI {
  async testTask() {
    return await this.requests.post<ServerTask>(`${routes.base}`, {});
  }

  async getAll() {
    return await this.requests.get<PaginationData<ServerTask>>(routes.base);
  }
}
