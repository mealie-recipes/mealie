import { BaseCRUDAPI } from "../_base";
import { CategoryIn, RecipeCategoryResponse } from "~/types/api-types/recipe";
import { config } from "~/api/config";

const prefix = config.PREFIX + "/organizers";

const routes = {
  categories: `${prefix}/categories`,
  categoriesId: (category: string) => `${prefix}/categories/${category}`,
  categoriesSlug: (category: string) => `${prefix}/categories/slug/${category}`,
};

export class CategoriesAPI extends BaseCRUDAPI<RecipeCategoryResponse, CategoryIn> {
  baseRoute: string = routes.categories;
  itemRoute = routes.categoriesId;

  async bySlug(slug: string) {
    return await this.requests.get<RecipeCategoryResponse>(routes.categoriesSlug(slug));
  }
}
