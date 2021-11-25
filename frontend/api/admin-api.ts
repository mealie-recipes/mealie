import { AdminAboutAPI } from "./admin/admin-about";
import { AdminTaskAPI } from "./admin/admin-tasks";
import { AdminUsersApi } from "./admin/admin-users";
import { AdminGroupsApi } from "./admin/admin-groups";
import { ApiRequestInstance } from "~/types/api";

export class AdminAPI {
  private static instance: AdminAPI;
  public about: AdminAboutAPI;
  public serverTasks: AdminTaskAPI;
  public users: AdminUsersApi;
  public groups: AdminGroupsApi;

  constructor(requests: ApiRequestInstance) {
    if (AdminAPI.instance instanceof AdminAPI) {
      return AdminAPI.instance;
    }

    this.about = new AdminAboutAPI(requests);
    this.serverTasks = new AdminTaskAPI(requests);
    this.users = new AdminUsersApi(requests);
    this.groups = new AdminGroupsApi(requests);

    Object.freeze(this);
    AdminAPI.instance = this;
  }
}
