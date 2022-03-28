import { BaseAPI } from "../_base";
import { SuccessResponse } from "~/types/api-types/response";
import { MaintenanceLogs, MaintenanceSummary } from "~/types/api-types/admin";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/maintenance`,
  logs: (lines: number) => `${prefix}/admin/maintenance/logs?lines=${lines}`,
  cleanImages: `${prefix}/admin/maintenance/clean/images`,
  cleanRecipeFolders: `${prefix}/admin/maintenance/clean/recipe-folders`,
  cleanLogFile: `${prefix}/admin/maintenance/clean/logs`,
};

export class AdminMaintenanceApi extends BaseAPI {
  async getInfo() {
    return this.requests.get<MaintenanceSummary>(routes.base);
  }

  async cleanImages() {
    return await this.requests.post<SuccessResponse>(routes.cleanImages, {});
  }

  async cleanRecipeFolders() {
    return await this.requests.post<SuccessResponse>(routes.cleanRecipeFolders, {});
  }

  async cleanLogFile() {
    return await this.requests.post<SuccessResponse>(routes.cleanLogFile, {});
  }

  async logs(lines: number) {
    return await this.requests.get<MaintenanceLogs>(routes.logs(lines));
  }
}
