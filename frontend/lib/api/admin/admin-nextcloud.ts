import { BaseAPI } from "../base/base-clients";

const routes = {
  base: "/api/admin/nextcloud",
  test: "/api/admin/nextcloud/test",
};

export interface NextcloudConfigResponse {
  enabled: boolean;
  url: string | null;
  username: string | null;
  taskList: string | null;
}

export interface NextcloudTestResponse {
  status: string;
  message: string | null;
  calendars: { slug: string; display_name: string }[] | null;
}

export class AdminNextcloudApi extends BaseAPI {
  async getConfig() {
    return await this.requests.get<NextcloudConfigResponse>(routes.base);
  }

  async testConnection() {
    return await this.requests.post<NextcloudTestResponse>(routes.test, {});
  }
}
