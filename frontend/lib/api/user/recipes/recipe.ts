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
  RecipeLastMade,
  RecipeSuggestionQuery,
  RecipeSuggestionResponse,
  RecipeTimelineEventIn,
  RecipeTimelineEventOut,
  RecipeTimelineEventUpdate,
} from "~/lib/api/types/recipe";
import { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";

export type Parser = "nlp" | "brute" | "openai";

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
  recipesSuggestions: `${prefix}/recipes/suggestions`,
  recipesTestScrapeUrl: `${prefix}/recipes/test-scrape-url`,
  recipesCreateUrl: `${prefix}/recipes/create/url`,
  recipesCreateUrlBulk: `${prefix}/recipes/create/url/bulk`,
  recipesCreateFromZip: `${prefix}/recipes/create/zip`,
  recipesCreateFromImage: `${prefix}/recipes/create/image`,
  recipesCreateFromHtmlOrJson: `${prefix}/recipes/create/html-or-json`,
  recipesCategory: `${prefix}/recipes/category`,
  recipesParseIngredient: `${prefix}/parser/ingredient`,
  recipesParseIngredients: `${prefix}/parser/ingredients`,
  recipesTimelineEvent: `${prefix}/recipes/timeline/events`,

  recipesRecipeSlug: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}`,
  recipesRecipeSlugExport: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports`,
  recipesRecipeSlugExportZip: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/exports/zip`,
  recipesRecipeSlugImage: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/image`,
  recipesRecipeSlugAssets: (recipe_slug: string) => `${prefix}/recipes/${recipe_slug}/assets`,

  recipesSlugComments: (slug: string) => `${prefix}/recipes/${slug}/comments`,
  recipesSlugCommentsId: (slug: string, id: number) => `${prefix}/recipes/${slug}/comments/${id}`,

  recipesSlugLastMade: (slug: string) => `${prefix}/recipes/${slug}/last-made`,
  recipesTimelineEventId: (id: string) => `${prefix}/recipes/timeline/events/${id}`,
  recipesTimelineEventIdImage: (id: string) => `${prefix}/recipes/timeline/events/${id}/image`,
};

export type RecipeSearchQuery = {
  search?: string;
  orderDirection?: "asc" | "desc";
  groupId?: string;

  queryFilter?: string;

  cookbook?: string;
  households?: string[];

  categories?: string[];
  requireAllCategories?: boolean;

  tags?: string[];
  requireAllTags?: boolean;

  tools?: string[];
  requireAllTools?: boolean;

  foods?: string[];
  requireAllFoods?: boolean;

  page?: number;
  perPage?: number;
  orderBy?: string;

  _searchSeed?: string;
};

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

  async search(rsq: RecipeSearchQuery) {
    return await this.requests.get<PaginationData<Recipe>>(route(routes.recipesBase, rsq));
  }

  async getAllByCategory(categories: string[]) {
    return await this.requests.get<Recipe[]>(routes.recipesCategory, {
      categories,
    });
  }

  async getSuggestions(q: RecipeSuggestionQuery, foods: string[] | null = null, tools: string[]| null = null) {
    return await this.requests.get<RecipeSuggestionResponse>(
      route(routes.recipesSuggestions, { ...q, foods, tools })
    );
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

  async testCreateOneUrl(url: string, useOpenAI = false) {
    return await this.requests.post<Recipe | null>(routes.recipesTestScrapeUrl, { url, useOpenAI });
  }

  async createOneByHtmlOrJson(data: string, includeTags: boolean) {
    return await this.requests.post<string>(routes.recipesCreateFromHtmlOrJson, { data, includeTags });
  }

  async createOneByUrl(url: string, includeTags: boolean) {
    return await this.requests.post<string>(routes.recipesCreateUrl, { url, includeTags });
  }

  async createManyByUrl(payload: CreateRecipeByUrlBulk) {
    return await this.requests.post<string>(routes.recipesCreateUrlBulk, payload);
  }

  async createOneFromImage(fileObject: Blob | File, fileName: string, translateLanguage: string | null = null) {
    const formData = new FormData();
    formData.append("images", fileObject);
    formData.append("extension", fileName.split(".").pop() ?? "");

    let apiRoute = routes.recipesCreateFromImage
    if (translateLanguage) {
      apiRoute = `${apiRoute}?translateLanguage=${translateLanguage}`
    }

    return await this.requests.post<string>(apiRoute, formData);
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

  async updateMany(payload: Recipe[]) {
    return await this.requests.put<Recipe[]>(routes.recipesBase, payload);
  }

  async patchMany(payload: Recipe[]) {
    return await this.requests.patch<Recipe[]>(routes.recipesBase, payload);
  }

  async updateLastMade(recipeSlug: string, timestamp: string) {
    return await this.requests.patch<Recipe, RecipeLastMade>(routes.recipesSlugLastMade(recipeSlug), { timestamp })
  }

  async createTimelineEvent(payload: RecipeTimelineEventIn) {
    return await this.requests.post<RecipeTimelineEventOut>(routes.recipesTimelineEvent, payload);
  }

  async updateTimelineEvent(eventId: string, payload: RecipeTimelineEventUpdate) {
    return await this.requests.put<RecipeTimelineEventOut, RecipeTimelineEventUpdate>(
      routes.recipesTimelineEventId(eventId),
      payload
    );
  }

  async deleteTimelineEvent(eventId: string) {
    return await this.requests.delete<RecipeTimelineEventOut>(routes.recipesTimelineEventId(eventId));
  }

  async getAllTimelineEvents(page = 1, perPage = -1, params = {} as any) {
    return await this.requests.get<PaginationData<RecipeTimelineEventOut>>(
      routes.recipesTimelineEvent,
      {
        params: { page, perPage, ...params },
      }
    );
  }

  async updateTimelineEventImage(eventId: string, fileObject: Blob | File, fileName: string) {
    const formData = new FormData();
    formData.append("image", fileObject);
    formData.append("extension", fileName.split(".").pop() ?? "");

    return await this.requests.put<UpdateImageResponse, FormData>(routes.recipesTimelineEventIdImage(eventId), formData);
  }
}
