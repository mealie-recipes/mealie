import { RecipeAPI } from "./class-interfaces/recipes";
import { UserApi } from "./class-interfaces/users";
import { ApiRequestInstance } from "~/types/api";

class Api {
  private static instance: Api;
  public recipes: RecipeAPI;
  public users: UserApi;

  constructor(requests: ApiRequestInstance) {
    if (Api.instance instanceof Api) {
      return Api.instance;
    }

    this.recipes = new RecipeAPI(requests);
    this.users = new UserApi(requests);

    Object.freeze(this);
    Api.instance = this;
  }
}

export { Api };
