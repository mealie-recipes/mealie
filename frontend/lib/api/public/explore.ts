import { BaseAPI } from "../base/base-clients";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";
import { PublicRecipeApi } from "./explore/recipes";
import { PublicFoodsApi } from "./explore/foods";
import { PublicCategoriesApi, PublicTagsApi, PublicToolsApi } from "./explore/organizers";

export class ExploreApi extends BaseAPI {
  public recipes: PublicRecipeApi;
  public foods: PublicFoodsApi;
  public categories: PublicCategoriesApi;
  public tags: PublicTagsApi;
  public tools: PublicToolsApi;

  constructor(requests: ApiRequestInstance, groupSlug: string) {
    super(requests);
    this.recipes = new PublicRecipeApi(requests, groupSlug);
    this.foods = new PublicFoodsApi(requests, groupSlug);
    this.categories = new PublicCategoriesApi(requests, groupSlug);
    this.tags = new PublicTagsApi(requests, groupSlug);
    this.tools = new PublicToolsApi(requests, groupSlug);
  }
}
