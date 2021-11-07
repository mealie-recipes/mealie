/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CreateRecipe {
  name: string;
}

export interface AllRecipeRequest {
  properties: string[];
  limit?: number;
}
export interface CategoryBase {
  name: string;
  id: number;
  slug: string;
}
export interface CategoryIn {
  name: string;
}
export interface CommentIn {
  text: string;
}
export interface CommentOut {
  text: string;
  id: number;
  uuid: string;
  recipeSlug: string;
  dateAdded: string;
  user: UserBase;
}
export interface UserBase {
  id: number;
  username?: string;
  admin: boolean;
}
export interface CommentSaveToDB {
  text: string;
  recipeSlug: string;
  user: number;
}
export interface Nutrition {
  calories?: string;
  fatContent?: string;
  proteinContent?: string;
  carbohydrateContent?: string;
  fiberContent?: string;
  sodiumContent?: string;
  sugarContent?: string;
}
export interface Recipe {
  id?: number;
  name: string;
  slug: string;
  image: string;
  description: string;
  recipeCategory: string[];
  tags: string[];
  rating: number;
  dateAdded: string;
  dateUpdated: string;
  recipeYield?: string;
  recipeIngredient: RecipeIngredient[];
  recipeInstructions: RecipeStep[];
  nutrition?: Nutrition;
  tools?: string[];
  totalTime?: string;
  prepTime?: string;
  performTime?: string;
  settings?: RecipeSettings;
  assets?: RecipeAsset[];
  notes?: RecipeNote[];
  orgURL?: string;
  extras?: {
    [k: string]: unknown;
  };
  comments?: CommentOut[];
}
export interface RecipeIngredient {
  referenceId: string;
  title: string;
  note: string;
  unit?: RecipeIngredientUnit | null;
  food?: RecipeIngredientFood | null;
  disableAmount: boolean;
  quantity: number;
}
export interface RecipeIngredientUnit {
  name?: string;
  description?: string;
  fraction?: boolean;
}
export interface RecipeIngredientFood {
  name?: string;
  description?: string;
}
export interface IngredientToStepRef {
  referenceId: string;
}
export interface RecipeStep {
  title?: string;
  text: string;
  ingredientReferences: IngredientToStepRef[];
}
export interface RecipeSettings {
  public?: boolean;
  showNutrition?: boolean;
  showAssets?: boolean;
  landscapeView?: boolean;
  disableComments?: boolean;
  disableAmount?: boolean;
}
export interface RecipeAsset {
  name: string;
  icon: string;
  fileName?: string;
}
export interface RecipeNote {
  title: string;
  text: string;
}
export interface RecipeSlug {
  slug: string;
}
export interface RecipeSummary {
  id?: number;
  name?: string;
  slug?: string;
  image?: unknown;
  description?: string;
  recipeCategory: string[];
  tags: string[];
  rating?: number;
  dateAdded?: string;
  dateUpdated?: string;
}
export interface RecipeURLIn {
  url: string;
}
export interface SlugResponse {}
export interface TagBase {
  name: string;
  id: number;
  slug: string;
}
export interface TagIn {
  name: string;
}
