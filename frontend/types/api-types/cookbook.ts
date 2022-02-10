/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CategoryBase {
  name: string;
  id: number;
  slug: string;
}
export interface CreateCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  categories?: CategoryBase[];
}
export interface ReadCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  categories?: CategoryBase[];
  groupId: string;
  id: number;
}
export interface RecipeCategoryResponse {
  name: string;
  id: number;
  slug: string;
  recipes?: Recipe[];
}
export interface Recipe {
  id?: string;
  userId?: string;
  groupId?: string;
  name?: string;
  slug?: string;
  image?: unknown;
  recipeYield?: string;
  totalTime?: string;
  prepTime?: string;
  cookTime?: string;
  performTime?: string;
  description?: string;
  recipeCategory?: RecipeCategory[];
  tags?: RecipeTag[];
  tools?: RecipeTool[];
  rating?: number;
  orgURL?: string;
  recipeIngredient?: RecipeIngredient[];
  dateAdded?: string;
  dateUpdated?: string;
  recipeInstructions?: RecipeStep[];
  nutrition?: Nutrition;
  settings?: RecipeSettings;
  assets?: RecipeAsset[];
  notes?: RecipeNote[];
  extras?: {
    [k: string]: unknown;
  };
  comments?: RecipeCommentOut[];
}
export interface RecipeCategory {
  id?: number;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: number;
  name: string;
  slug: string;
}
export interface RecipeTool {
  id?: number;
  name: string;
  slug: string;
  onHand?: boolean;
}
export interface RecipeIngredient {
  title?: string;
  note?: string;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  disableAmount?: boolean;
  quantity?: number;
  referenceId?: string;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: number;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
}
export interface IngredientFood {
  name: string;
  description?: string;
  labelId?: string;
  id: number;
  label?: MultiPurposeLabelSummary;
}
export interface MultiPurposeLabelSummary {
  name: string;
  color?: string;
  groupId: string;
  id: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
  labelId?: string;
}
export interface RecipeStep {
  id?: string;
  title?: string;
  text: string;
  ingredientReferences?: IngredientReferences[];
}
/**
 * A list of ingredient references.
 */
export interface IngredientReferences {
  referenceId?: string;
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
export interface RecipeSettings {
  public?: boolean;
  showNutrition?: boolean;
  showAssets?: boolean;
  landscapeView?: boolean;
  disableComments?: boolean;
  disableAmount?: boolean;
  locked?: boolean;
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
export interface RecipeCommentOut {
  recipeId: string;
  text: string;
  id: string;
  createdAt: string;
  updateAt: string;
  userId: string;
  user: UserBase;
}
export interface UserBase {
  id: number;
  username?: string;
  admin: boolean;
}
export interface RecipeCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  categories: RecipeCategoryResponse[];
  groupId: string;
  id: number;
}
export interface SaveCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  categories?: CategoryBase[];
  groupId: string;
}
export interface UpdateCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  categories?: CategoryBase[];
  groupId: string;
  id: number;
}
