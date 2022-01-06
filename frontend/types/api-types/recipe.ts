/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type RegisteredParser = "nlp" | "brute";

export interface CategoryBase {
  name: string;
  id: number;
  slug: string;
}
export interface CategoryIn {
  name: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
}
export interface CreateRecipe {
  name: string;
}
export interface CreateRecipeBulk {
  url: string;
  categories?: RecipeCategory[];
  tags?: RecipeTag[];
}
export interface RecipeCategory {
  name: string;
  slug: string;
}
export interface RecipeTag {
  name: string;
  slug: string;
}
export interface CreateRecipeByUrl {
  url: string;
}
export interface CreateRecipeByUrlBulk {
  imports: CreateRecipeBulk[];
}
export interface IngredientConfidence {
  average?: number;
  comment?: number;
  name?: number;
  unit?: number;
  quantity?: number;
  food?: number;
}
export interface IngredientFood {
  name: string;
  description?: string;
  id: number;
}
export interface IngredientRequest {
  parser?: RegisteredParser & string;
  ingredient: string;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: number;
}
export interface IngredientsRequest {
  parser?: RegisteredParser & string;
  ingredients: string[];
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
export interface ParsedIngredient {
  input?: string;
  confidence?: IngredientConfidence;
  ingredient: RecipeIngredient;
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
export interface Recipe {
  id?: number;
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
  recipeCategory?: RecipeTag[];
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
export interface RecipeTool {
  name: string;
  slug: string;
  id?: number;
  onHand?: boolean;
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
  recipeId: number;
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
export interface RecipeCategoryResponse {
  name: string;
  id: number;
  slug: string;
  recipes?: Recipe[];
}
export interface RecipeCommentCreate {
  recipeId: number;
  text: string;
}
export interface RecipeCommentSave {
  recipeId: number;
  text: string;
  userId: string;
}
export interface RecipeCommentUpdate {
  id: string;
  text: string;
}
export interface RecipeSlug {
  slug: string;
}
export interface RecipeSummary {
  id?: number;
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
  recipeCategory?: RecipeTag[];
  tags?: RecipeTag[];
  tools?: RecipeTool[];
  rating?: number;
  orgURL?: string;
  recipeIngredient?: RecipeIngredient[];
  dateAdded?: string;
  dateUpdated?: string;
}
export interface RecipeTagResponse {
  name: string;
  id: number;
  slug: string;
  recipes?: Recipe[];
}
export interface RecipeTool1 {
  name: string;
  onHand?: boolean;
  id: number;
  slug: string;
}
export interface RecipeToolCreate {
  name: string;
  onHand?: boolean;
}
export interface RecipeToolResponse {
  name: string;
  onHand?: boolean;
  id: number;
  slug: string;
  recipes?: Recipe[];
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
