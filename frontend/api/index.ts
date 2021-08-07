import { RecipeAPI } from "./class-interfaces/recipes";
import { UserApi } from "./class-interfaces/users";
import { GroupAPI } from "./class-interfaces/groups";
import { ApiRequestInstance } from "~/types/api";

class Api {
  private static instance: Api;
  public recipes: RecipeAPI;
  public users: UserApi;
  public groups: GroupAPI;

  constructor(requests: ApiRequestInstance) {
    if (Api.instance instanceof Api) {
      return Api.instance;
    }

    this.recipes = new RecipeAPI(requests);
    this.users = new UserApi(requests);
    this.groups = new GroupAPI(requests);

    Object.freeze(this);
    Api.instance = this;
  }
}

export { Api };
