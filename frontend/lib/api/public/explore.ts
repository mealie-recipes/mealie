import { BaseAPI } from "../base/base-clients";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";
import { PublicRecipeApi } from "./explore/recipes";

export class ExploreApi extends BaseAPI {
  public recipes: PublicRecipeApi;

  constructor(requests: ApiRequestInstance, groupSlug: string) {
    super(requests);
    this.recipes = new PublicRecipeApi(requests, groupSlug);
  }
}
