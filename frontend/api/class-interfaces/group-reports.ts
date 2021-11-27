import { BaseAPI } from "../_base";

const prefix = "/api";

export type ReportCategory = "backup" | "restore" | "migration";

export type SummaryStatus = "success" | "failure" | "partial" | "in-progress";

export interface ReportEntry {
  id: string;
  reportId: string;
  timestamp: Date;
  success: boolean;
  message: string;
  exception: string;
}

export interface ReportSummary {
  id: string;
  timestamp: Date;
  category: ReportCategory;
  groupId: number;
  name: string;
  status: SummaryStatus;
}

export interface Report extends ReportSummary {
  entries: ReportEntry[];
}

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
    return await this.requests.get<Report>(routes.getOne(id));
  }

  async deleteOne(id: string) {
    return await this.requests.delete(routes.getOne(id));
  }
}
