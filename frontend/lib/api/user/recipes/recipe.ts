import { BaseCRUDAPI } from "../../base/base-clients";
import { route } from "../../base";
import { CommentsApi } from "./recipe-comments";
import { RecipeShareApi } from "./recipe-share";
import {
  Recipe,
  CreateRecipe,
  RecipeAsset,
  CreateRecipeByUrlBulk,
  ParsedIngredient,
  UpdateImageResponse,
  RecipeZipTokenResponse,
  RecipeTimelineEventIn,
  RecipeTimelineEventOut,
  RecipeTimelineEventUpdate,
} from "~/lib/api/types/recipe";
import { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";

export type Parser = "nlp" | "brute";

export interface CreateAsset {
  name: string;
  icon: string;
  extension: string;
  file: File;
}

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
  recipesCreateFromOcr: `${prefix}/recipes/create-ocr`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugExport: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports`,
  recipesRecipeSlugExportZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,

  recipesSlugComments: (slug: string) => `${prefix}/recipes/${slug}/comments`,
  recipesSlugCommentsId: (slug: string, id: number) => `${prefix}/recipes/${slug}/comments/${id}`,

  recipesSlugTimelineEvent: (slug: string) => `${prefix}/recipes/${slug}/timeline/events`,
  recipesSlugTimelineEventId: (slug: string, id: string) => `${prefix}/recipes/${slug}/timeline/events/${id}`,
};

export type RecipeSearchQuery ={
  search: string;
  orderDirection? : "asc" | "desc";
  groupId?: string;

  queryFilter?: string;

  cookbook?: string;

  categories?: string[];
  requireAllCategories?: boolean;

  tags?: string[];
  requireAllTags?: boolean;

  tools?: string[];
  requireAllTools?: boolean;

  page: number;
  perPage: number;
  orderBy?: string;
}


export class RecipeAPI extends BaseCRUDAPI<CreateRecipe, Recipe, Recipe> {
  baseRoute: string = routes.recipesBase;
  itemRoute = routes.recipesRecipeSlug;

  comments: CommentsApi;
  share: RecipeShareApi;

  constructor(requests: ApiRequestInstance) {
    super(requests);

    this.comments = new CommentsApi(requests);
    this.share = new RecipeShareApi(requests);
  }

  async search(rsq : RecipeSearchQuery) {
    return await this.requests.get<PaginationData<Recipe>>(route(routes.recipesBase, rsq));
  }

  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories,
    });
  }

  async createAsset(recipeSlug: string, payload: CreateAsset) {
    const formData = new FormData();
    formData.append("file", payload.file);
    formData.append("name", payload.name);
    formData.append("extension", payload.extension);
    formData.append("icon", payload.icon);

    return await this.requests.post<RecipeAsset>(routes.recipesRecipeSlugAssets(recipeSlug), formData);
  }

  updateImage(slug: string, fileObject: File) {
    const formData = new FormData();
    formData.append("image", fileObject);
    formData.append("extension", fileObject.name.split(".").pop() ?? "");

    return this.requests.put<UpdateImageResponse, FormData>(routes.recipesRecipeSlugImage(slug), formData);
  }

  updateImagebyURL(slug: string, url: string) {
    return this.requests.post<UpdateImageResponse>(routes.recipesRecipeSlugImage(slug), { url });
  }

  async testCreateOneUrl(url: string) {
    return await this.requests.post<Recipe | null>(routes.recipesTestScrapeUrl, { url });
  }

  async createOneByUrl(url: string, includeTags: boolean) {
    return await this.requests.post<string>(routes.recipesCreateUrl, { url, includeTags });
  }

  async createManyByUrl(payload: CreateRecipeByUrlBulk) {
    return await this.requests.post<string>(routes.recipesCreateUrlBulk, payload);
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
    return await this.requests.post<RecipeZipTokenResponse>(routes.recipesRecipeSlugExport(recipeSlug), {});
  }

  getZipRedirectUrl(recipeSlug: string, token: string) {
    return `${routes.recipesRecipeSlugExportZip(recipeSlug)}?token=${token}`;
  }

  async createFromOcr(file: File, makeFileRecipeImage: boolean) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("extension", file.name.split(".").pop() ?? "");
    formData.append("makefilerecipeimage", String(makeFileRecipeImage));

    return await this.requests.post(routes.recipesCreateFromOcr, formData);
  }

  async createTimelineEvent(recipeSlug: string, payload: RecipeTimelineEventIn) {
    return await this.requests.post<RecipeTimelineEventOut>(routes.recipesSlugTimelineEvent(recipeSlug), payload);
  }

  async updateTimelineEvent(recipeSlug: string, eventId: string, payload: RecipeTimelineEventUpdate) {
    return await this.requests.put<RecipeTimelineEventOut, RecipeTimelineEventUpdate>(routes.recipesSlugTimelineEventId(recipeSlug, eventId), payload);
  }

  async deleteTimelineEvent(recipeSlug: string, eventId: string) {
    return await this.requests.delete<RecipeTimelineEventOut>(routes.recipesSlugTimelineEventId(recipeSlug, eventId));
  }

  async getAllTimelineEvents(recipeSlug: string, page = 1, perPage = -1, params = {} as any) {
    return await this.requests.get<PaginationData<RecipeTimelineEventOut>>(routes.recipesSlugTimelineEvent(recipeSlug), {
      params: { page, perPage, ...params },
    });
  }
}
