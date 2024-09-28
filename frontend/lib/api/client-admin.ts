import { AdminAboutAPI } from "./admin/admin-about";
import { AdminUsersApi } from "./admin/admin-users";
import { AdminHouseholdsApi } from "./admin/admin-households";
import { AdminGroupsApi } from "./admin/admin-groups";
import { AdminBackupsApi } from "./admin/admin-backups";
import { AdminMaintenanceApi } from "./admin/admin-maintenance";
import { AdminAnalyticsApi } from "./admin/admin-analytics";
import { AdminDebugAPI } from "./admin/admin-debug";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

export class AdminAPI {
  public about: AdminAboutAPI;
  public users: AdminUsersApi;
  public households: AdminHouseholdsApi;
  public groups: AdminGroupsApi;
  public backups: AdminBackupsApi;
  public maintenance: AdminMaintenanceApi;
  public analytics: AdminAnalyticsApi;
  public debug: AdminDebugAPI;

  constructor(requests: ApiRequestInstance) {
    this.about = new AdminAboutAPI(requests);
    this.users = new AdminUsersApi(requests);
    this.households = new AdminHouseholdsApi(requests);
    this.groups = new AdminGroupsApi(requests);
    this.backups = new AdminBackupsApi(requests);
    this.maintenance = new AdminMaintenanceApi(requests);
    this.analytics = new AdminAnalyticsApi(requests);
    this.debug = new AdminDebugAPI(requests);

    Object.freeze(this);
  }
}
