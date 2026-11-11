import { BaseAPI } from "../base/base-clients";
import type { SuccessResponse } from "~/lib/api/types/response";
import type { MaintenanceStorageDetails, MaintenanceSummary } from "~/lib/api/types/admin";

const prefix = "/api";

const routes = {
  base: `${prefix}/admin/maintenance`,
  storage: `${prefix}/admin/maintenance/storage`,
  cleanTemp: `${prefix}/admin/maintenance/clean/temp`,
  cleanImages: `${prefix}/admin/maintenance/clean/images`,
  cleanRecipeFolders: `${prefix}/admin/maintenance/clean/recipe-folders`,
};

export class AdminMaintenanceApi extends BaseAPI {
  async getInfo() {
    return this.requests.get<MaintenanceSummary>(routes.base);
  }

  async getStorageDetails() {
    return await this.requests.get<MaintenanceStorageDetails>(routes.storage);
  }

  async cleanTemp() {
    return await this.requests.post<SuccessResponse>(routes.cleanTemp, {});
  }

  async cleanImages() {
    return await this.requests.post<SuccessResponse>(routes.cleanImages, {});
  }

  async cleanRecipeFolders() {
    return await this.requests.post<SuccessResponse>(routes.cleanRecipeFolders, {});
  }
}
