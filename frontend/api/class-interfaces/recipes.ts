import { BaseAPIClass } from "./_base";
import { Recipe } from "~/types/api-types/admin";

const prefix = "/api";

const routes = {
  recipesCreate: `${prefix}/recipes/create`,
  recipesBase: `${prefix}/recipes`,
  recipesSummary: `${prefix}/recipes/summary`,
  recipesTestScrapeUrl: `${prefix}/recipes/test-scrape-url`,
  recipesCreateUrl: `${prefix}/recipes/create-url`,
  recipesCreateFromZip: `${prefix}/recipes/create-from-zip`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,
};

class RecipeAPI extends BaseAPIClass {
  async getAll(start = 0, limit = 9999) {
    return await this.requests.get<Recipe[]>(routes.recipesSummary, {
      params: { start, limit },
    });
  }

  async getOne(slug: string) {
    return await this.requests.get<Recipe>(routes.recipesRecipeSlug(slug));
  }

  async createOne(name: string) {
    return await this.requests.post(routes.recipesBase, { name });
  }




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
}

export { RecipeAPI };
