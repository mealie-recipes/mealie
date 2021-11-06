import { BaseCRUDAPI } from "../_base";
import { Category } from "./categories";
import { Tag } from "./tags";
import { Recipe, CreateRecipe } from "~/types/api-types/recipe";

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
};

export type Parser = "nlp" | "brute";

export interface Confidence {
  average?: number;
  comment?: number;
  name?: number;
  unit?: number;
  quantity?: number;
  food?: number;
}

export interface Unit {
  name: string;
  description: string;
  fraction: boolean;
  abbreviation: string;
}

export interface Food {
  name: string;
  description?: string;
}

export interface Ingredient {
  referenceId: string;
  title: string;
  note: string;
  unit: Unit | null;
  food: Food | null;
  disableAmount: boolean;
  quantity: number;
}

export interface ParsedIngredient {
  confidence: Confidence;
  ingredient: Ingredient;
}

export interface BulkCreateRecipe {
  url: string;
  categories: Category[];
  tags: Tag[];
}

export interface BulkCreatePayload {
  imports: BulkCreateRecipe[];
}

export interface RecipeZipToken {
  token: string;
}

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

  async testCreateOneUrl(url: string) {
    return await this.requests.post<Recipe | null>(routes.recipesTestScrapeUrl, { url });
  }

  async createOneByUrl(url: string) {
    return await this.requests.post(routes.recipesCreateUrl, { url });
  }

  async createManyByUrl(payload: BulkCreatePayload) {
    return await this.requests.post(routes.recipesCreateUrlBulk, payload);
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
}
