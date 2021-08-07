import { RecipeAPI } from "./class-interfaces/recipes";
import { UserApi } from "./class-interfaces/users";
import { GroupAPI } from "./class-interfaces/groups";
import { DebugAPI } from "./class-interfaces/debug";
import { EventsAPI } from "./class-interfaces/events";
import { BackupAPI } from "./class-interfaces/backups";
import { UploadFile } from "./class-interfaces/upload";
import { ApiRequestInstance } from "~/types/api";

class Api {
  private static instance: Api;
  public recipes: RecipeAPI;
  public users: UserApi;
  public groups: GroupAPI;
  public debug: DebugAPI;
  public events: EventsAPI;
  public backups: BackupAPI;
  public upload: UploadFile;

  constructor(requests: ApiRequestInstance) {
    if (Api.instance instanceof Api) {
      return Api.instance;
    }

    this.recipes = new RecipeAPI(requests);
    this.users = new UserApi(requests);
    this.groups = new GroupAPI(requests);
    this.debug = new DebugAPI(requests);
    this.events = new EventsAPI(requests);
    this.backups = new BackupAPI(requests);
    this.upload = new UploadFile(requests);

    Object.freeze(this);
    Api.instance = this;
  }
}

export { Api };
