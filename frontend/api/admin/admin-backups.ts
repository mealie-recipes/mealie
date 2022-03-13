import { BaseAPI } from "../_base";
import { AllBackups } from "~/types/api-types/admin";
import { ErrorResponse, FileTokenResponse, SuccessResponse } from "~/types/api-types/response";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/backups`,
  item: (name: string) => `${prefix}/admin/backups/${name}`,
  restore: (name: string) => `${prefix}/admin/backups/${name}/restore`,
};

export class AdminBackupsApi extends BaseAPI {
  async getAll() {
    return await this.requests.get<AllBackups>(routes.base);
  }

  async create() {
    return await this.requests.post<SuccessResponse | ErrorResponse>(routes.base, {});
  }

  async get(fileName: string) {
    return await this.requests.get<FileTokenResponse>(routes.item(fileName));
  }

  async delete(fileName: string) {
    return await this.requests.delete<SuccessResponse | ErrorResponse>(routes.item(fileName));
  }

  async restore(fileName: string) {
    return await this.requests.post<SuccessResponse | ErrorResponse>(routes.restore(fileName), {});
  }
}
