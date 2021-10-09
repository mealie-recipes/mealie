import { BaseCRUDAPI } from "./_base";
import { Recipe, CreateRecipe } from "~/types/api-types/recipe";

const prefix = "/api";

const routes = {
  recipesCreate: `${prefix}/recipes/create`,
  recipesBase: `${prefix}/recipes`,
  recipesTestScrapeUrl: `${prefix}/recipes/test-scrape-url`,
  recipesCreateUrl: `${prefix}/recipes/create-url`,
  recipesCreateFromZip: `${prefix}/recipes/create-from-zip`,
  recipesCategory: `${prefix}/recipes/category`,
  recipesParseIngredient: `${prefix}/parser/ingredient`,
  recipesParseIngredients: `${prefix}/parser/ingredients`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,

  recipesSlugComments: (slug: string) => `${prefix}/recipes/${slug}/comments`,
  recipesSlugCommentsId: (slug: string, id: number) => `${prefix}/recipes/${slug}/comments/${id}`,
};

export class RecipeAPI extends BaseCRUDAPI<Recipe, CreateRecipe> {
  baseRoute: string = routes.recipesBase;
  itemRoute = routes.recipesRecipeSlug;

  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories,
    });
  }

  updateImage(slug: string, fileObject: File) {
    const formData = new FormData();
    formData.append("image", fileObject);
    // @ts-ignore
    formData.append("extension", fileObject.name.split(".").pop());

    return this.requests.put<any>(routes.recipesRecipeSlugImage(slug), formData);
  }

  updateImagebyURL(slug: string, url: string) {
    return this.requests.post(routes.recipesRecipeSlugImage(slug), { url });
  }

  async createOneByUrl(url: string) {
    return await this.requests.post(routes.recipesCreateUrl, { url });
  }

  // Recipe Comments

  // Methods to Generate reference urls for assets/images *
  recipeImage(recipeSlug: string, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/original.webp?&rnd=${key}&version=${version}`;
  }

  recipeSmallImage(recipeSlug: string, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/min-original.webp?&rnd=${key}&version=${version}`;
  }

  recipeTinyImage(recipeSlug: string, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/tiny-original.webp?&rnd=${key}&version=${version}`;
  }

  recipeAssetPath(recipeSlug: string, assetName: string) {
    return `/api/media/recipes/${recipeSlug}/assets/${assetName}`;
  }

  async createComment(slug: string, payload: Object) {
    return await this.requests.post(routes.recipesSlugComments(slug), payload);
  }

  /** Update comment in the Database
   */
  async updateComment(slug: string, id: number, payload: Object) {
    return await this.requests.put(routes.recipesSlugCommentsId(slug, id), payload);
  }

  /** Delete comment from the Database
   */
  async deleteComment(slug: string, id: number) {
    return await this.requests.delete(routes.recipesSlugCommentsId(slug, id));
  }

  async parseIngredients(ingredients: Array<string>) {
    return await this.requests.post(routes.recipesParseIngredients, { ingredients });
  }

  async parseIngredient(ingredient: string) {
    return await this.requests.post(routes.recipesParseIngredient, { ingredient });
  }
}
