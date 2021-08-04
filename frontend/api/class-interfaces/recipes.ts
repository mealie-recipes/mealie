import { BaseAPIClass, crudMixins } from "./_base";
import { Recipe } from "~/types/api-types/admin";
import { ApiRequestInstance } from "~/types/api";

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

export class RecipeAPI extends BaseAPIClass<Recipe> {
  baseRoute: string = routes.recipesSummary;
  itemRoute = routes.recipesRecipeSlug;

  constructor(requests: ApiRequestInstance) {
    super(requests);
    const { getAll, getOne, updateOne, patchOne, deleteOne } = crudMixins<Recipe>(
      requests,
      routes.recipesSummary,
      routes.recipesRecipeSlug
    );

    this.getAll = getAll;
    this.getOne = getOne;
    this.updateOne = updateOne;
    this.patchOne = patchOne;
    this.deleteOne = deleteOne;
  }

  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories,
    });
  }

  updateImage(slug: string, fileObject: File) {
    const formData = new FormData();
    formData.append("image", fileObject);
    formData.append("extension", fileObject.name.split(".").pop());

    return this.requests.put<any>(routes.recipesRecipeSlugImage(slug), formData);
  }

  updateImagebyURL(slug: string, url: string) {
    return this.requests.post(routes.recipesRecipeSlugImage(slug), { url });
  }

  async createOne(name: string) {
    return await this.requests.post<Recipe>(routes.recipesBase, { name });
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
