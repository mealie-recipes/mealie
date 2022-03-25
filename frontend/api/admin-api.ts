import { AdminAboutAPI } from "./admin/admin-about";
import { AdminTaskAPI } from "./admin/admin-tasks";
import { AdminUsersApi } from "./admin/admin-users";
import { AdminGroupsApi } from "./admin/admin-groups";
import { AdminBackupsApi } from "./admin/admin-backups";
import { AdminMaintenanceApi } from "./admin/admin-maintenance";
import { ApiRequestInstance } from "~/types/api";

export class AdminAPI {
  public about: AdminAboutAPI;
  public serverTasks: AdminTaskAPI;
  public users: AdminUsersApi;
  public groups: AdminGroupsApi;
  public backups: AdminBackupsApi;
  public maintenance: AdminMaintenanceApi;

  constructor(requests: ApiRequestInstance) {
    this.about = new AdminAboutAPI(requests);
    this.serverTasks = new AdminTaskAPI(requests);
    this.users = new AdminUsersApi(requests);
    this.groups = new AdminGroupsApi(requests);
    this.backups = new AdminBackupsApi(requests);
    this.maintenance = new AdminMaintenanceApi(requests);

    Object.freeze(this);
  }
}
