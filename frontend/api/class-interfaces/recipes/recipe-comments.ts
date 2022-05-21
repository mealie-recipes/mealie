import { BaseCRUDAPI } from "~/api/_base";
import { RecipeCommentCreate, RecipeCommentOut, RecipeCommentUpdate } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  comment: `${prefix}/comments`,
  byRecipe: (id: string) => `${prefix}/recipes/${id}/comments`,
  commentsId: (id: string) => `${prefix}/comments/${id}`,
};

export class CommentsApi extends BaseCRUDAPI<RecipeCommentCreate, RecipeCommentOut, RecipeCommentUpdate> {
  baseRoute: string = routes.comment;
  itemRoute = routes.commentsId;

  async byRecipe(slug: string) {
    return await this.requests.get<RecipeCommentOut[]>(routes.byRecipe(slug));
  }
}
