import { CreateAsset, ParsedIngredient, Parser, RecipeZipToken, BulkCreatePayload } from "./types";
import { CommentsApi } from "./recipe-comments";
import { RecipeShareApi } from "./recipe-share";
import { BaseCRUDAPI } from "~/api/_base";

import { Recipe, CreateRecipe } from "~/types/api-types/recipe";
import { ApiRequestInstance } from "~/types/api";

const prefix = "/api";

const routes = {
  recipesCreate: `${prefix}/recipes/create`,
  recipesBase: `${prefix}/recipes`,
  recipesTestScrapeUrl: `${prefix}/recipes/test-scrape-url`,
  recipesCreateUrl: `${prefix}/recipes/create-url`,
  recipesCreateUrlBulk: `${prefix}/recipes/create-url/bulk`,
  recipesCreateFromZip: `${prefix}/recipes/create-from-zip`,
  recipesCategory: `${prefix}/recipes/category`,
  recipesParseIngredient: `${prefix}/parser/ingredient`,
  recipesParseIngredients: `${prefix}/parser/ingredients`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugExport: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports`,
  recipesRecipeSlugExportZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,

  recipesSlugComments: (slug: string) => `${prefix}/recipes/${slug}/comments`,
  recipesSlugCommentsId: (slug: string, id: number) => `${prefix}/recipes/${slug}/comments/${id}`,

  recipeShareToken: (token: string) => `${prefix}/recipes/shared/${token}`,
};

export class RecipeAPI extends BaseCRUDAPI<Recipe, CreateRecipe> {
  baseRoute: string = routes.recipesBase;
  itemRoute = routes.recipesRecipeSlug;

  comments: CommentsApi;
  share: RecipeShareApi;

  constructor(requests: ApiRequestInstance) {
    super(requests);

    this.comments = new CommentsApi(requests);
    this.share = new RecipeShareApi(requests);
  }

  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories,
    });
  }

  async createAsset(recipeSlug: string, payload: CreateAsset) {
    const formData = new FormData();
    // @ts-ignore
    formData.append("file", payload.file);
    formData.append("name", payload.name);
    formData.append("extension", payload.extension);
    formData.append("icon", payload.icon);

    return await this.requests.post(routes.recipesRecipeSlugAssets(recipeSlug), formData);
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

  async testCreateOneUrl(url: string) {
    return await this.requests.post<Recipe | null>(routes.recipesTestScrapeUrl, { url });
  }

  async createOneByUrl(url: string) {
    return await this.requests.post(routes.recipesCreateUrl, { url });
  }

  async createManyByUrl(payload: BulkCreatePayload) {
    return await this.requests.post(routes.recipesCreateUrlBulk, payload);
  }

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

  async parseIngredients(parser: Parser, ingredients: Array<string>) {
    parser = parser || "nlp";
    return await this.requests.post<ParsedIngredient[]>(routes.recipesParseIngredients, { parser, ingredients });
  }

  async parseIngredient(parser: Parser, ingredient: string) {
    parser = parser || "nlp";
    return await this.requests.post<ParsedIngredient>(routes.recipesParseIngredient, { parser, ingredient });
  }

  async getZipToken(recipeSlug: string) {
    return await this.requests.post<RecipeZipToken>(routes.recipesRecipeSlugExport(recipeSlug), {});
  }

  getZipRedirectUrl(recipeSlug: string, token: string) {
    return `${routes.recipesRecipeSlugExportZip(recipeSlug)}?token=${token}`;
  }

  async getShared(item_id: string) {
    return await this.requests.get<Recipe>(routes.recipeShareToken(item_id));
  }
}
