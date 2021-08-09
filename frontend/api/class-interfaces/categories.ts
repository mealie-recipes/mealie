import { BaseCRUDAPI } from "./_base";

const prefix = "/api";

export interface Category {
  name: string;
  id: number;
  slug: string;
}

export interface CreateCategory {
  name: string;
}

const routes = {
  categories: `${prefix}/categories`,
  categoriesEmpty: `${prefix}/categories/empty`,

  categoriesCategory: (category: string) => `${prefix}/categories/${category}`,
};

export class CategoriesAPI extends BaseCRUDAPI<Category, CreateCategory> {
  baseRoute: string = routes.categories;
  itemRoute = routes.categoriesCategory;

  /** Returns a list of categories that do not contain any recipes
   */
  async getEmptyCategories() {
    return await this.requests.get(routes.categoriesEmpty);
  }

  /** Returns a list of recipes associated with the provided category.
   */
  async getAllRecipesByCategory(category: string) {
    return await this.requests.get(routes.categoriesCategory(category));
  }

  /** Removes a recipe category from the database. Deleting a
   * category does not impact a recipe. The category will be removed
   * from any recipes that contain it
   */
  async deleteRecipeCategory(category: string) {
    return await this.requests.delete(routes.categoriesCategory(category));
  }
}
