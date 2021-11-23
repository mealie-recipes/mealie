import { RecipeComment, RecipeCommentCreate } from "./types";
import { BaseCRUDAPI } from "~/api/_base";

const prefix = "/api";

const routes = {
  comment: `${prefix}/comments`,
  byRecipe: (id: string) => `${prefix}/recipes/${id}/comments`,
  commentsId: (id: string) => `${prefix}/comments/${id}`,
};

export class CommentsApi extends BaseCRUDAPI<RecipeComment, RecipeCommentCreate> {
  baseRoute: string = routes.comment;
  itemRoute = routes.commentsId;

  async byRecipe(slug: string) {
    return await this.requests.get<RecipeComment[]>(routes.byRecipe(slug));
  }
}
