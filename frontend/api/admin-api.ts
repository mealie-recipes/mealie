import { AdminAboutAPI } from "./admin/admin-about";
import { AdminTaskAPI } from "./admin/admin-tasks";
import { ApiRequestInstance } from "~/types/api";

export class AdminAPI {
  private static instance: AdminAPI;
  public about: AdminAboutAPI;
  public serverTasks: AdminTaskAPI;

  constructor(requests: ApiRequestInstance) {
    if (AdminAPI.instance instanceof AdminAPI) {
      return AdminAPI.instance;
    }

    this.about = new AdminAboutAPI(requests);
    this.serverTasks = new AdminTaskAPI(requests);

    Object.freeze(this);
    AdminAPI.instance = this;
  }
}
