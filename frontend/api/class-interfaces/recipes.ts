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

  recipesCategory: `${prefix}/recipes/category`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,
};

class RecipeAPI extends BaseAPIClass<Recipe> {
  baseRoute: string = routes.recipesSummary;
  itemRoute = (itemid: string) => routes.recipesRecipeSlug(itemid);


  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories
    });
  }

  // @ts-ignore - Override method doesn't take same arguments are parent class
  async createOne(name: string) {
    return await this.requests.post(routes.recipesBase, { name });
  }

  async createOneByUrl(url: string) {
    return await this.requests.post(routes.recipesCreateUrl, { url });
  }

  // * Methods to Generate reference urls for assets/images *
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
