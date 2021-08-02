import { RecipeAPI } from "./class-interfaces/recipes";
import { ApiRequestInstance } from "~/types/api";

class Api {
  private static instance: Api;
  public recipes: RecipeAPI;

  constructor(requests: ApiRequestInstance) {
    if (Api.instance instanceof Api) {
      return Api.instance;
    }

    this.recipes = new RecipeAPI(requests);

    Object.freeze(this);
    Api.instance = this;
  }
}

export { Api };
