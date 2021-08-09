import { BaseCRUDAPI } from "./_base";

const prefix = "/api";

export interface Tag {
  name: string;
  id: number;
  slug: string;
}

export interface CreateTag {
  name: string;
}

const routes = {
  tags: `${prefix}/tags`,
  tagsEmpty: `${prefix}/tags/empty`,

  tagsTag: (tag: string) => `${prefix}/tags/${tag}`,
};

export class TagsAPI extends BaseCRUDAPI<Tag, CreateTag> {
  baseRoute: string = routes.tags;
  itemRoute = routes.tagsTag;

  /** Returns a list of categories that do not contain any recipes
   */
  async getEmptyCategories() {
    return await this.requests.get(routes.tagsEmpty);
  }

  /** Returns a list of recipes associated with the provided category.
   */
  async getAllRecipesByCategory(category: string) {
    return await this.requests.get(routes.tagsTag(category));
  }

  /** Removes a recipe category from the database. Deleting a
   * category does not impact a recipe. The category will be removed
   * from any recipes that contain it
   */
  async deleteRecipeCategory(category: string) {
    return await this.requests.delete(routes.tagsTag(category));
  }
}
