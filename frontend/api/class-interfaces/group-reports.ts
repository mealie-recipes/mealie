import { BaseAPI } from "../_base";
import { ReportCategory, ReportOut, ReportSummary } from "~/types/api-types/reports";

const prefix = "/api";

const routes = {
  base: `${prefix}/groups/reports`,
  getOne: (id: string) => `${prefix}/groups/reports/${id}`,
};

export class GroupReportsApi extends BaseAPI {
  async getAll(category: ReportCategory | null) {
    const query = category ? `?report_type=${category}` : "";
    return await this.requests.get<ReportSummary[]>(routes.base + query);
  }

  async getOne(id: string) {
    return await this.requests.get<ReportOut>(routes.getOne(id));
  }

  async deleteOne(id: string) {
    return await this.requests.delete(routes.getOne(id));
  }
}
