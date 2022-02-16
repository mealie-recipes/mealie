/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CategoryBase {
  name: string;
  id: string;
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
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeSummary {
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
}
export interface RecipeCategory {
  id: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id: string;
  name: string;
  slug: string;
}
export interface RecipeTool {
  id: string;
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
  id: string;
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
  id: string;
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
