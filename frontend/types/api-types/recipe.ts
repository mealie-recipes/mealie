/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ExportTypes = "json";
export type RegisteredParser = "nlp" | "brute";

export interface AssignCategories {
  recipes: string[];
  categories: CategoryBase[];
}
export interface CategoryBase {
  name: string;
  id: string;
  slug: string;
}
export interface AssignTags {
  recipes: string[];
  tags: TagBase[];
}
export interface TagBase {
  name: string;
  id: string;
  slug: string;
}
export interface BulkActionError {
  recipe: string;
  error: string;
}
export interface BulkActionsResponse {
  success: boolean;
  message: string;
  errors?: BulkActionError[];
}
export interface CategoryIn {
  name: string;
}
export interface CategoryOut {
  name: string;
  id: string;
  slug: string;
}
export interface CategorySave {
  name: string;
  groupId: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
  labelId?: string;
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
  id: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id: string;
  name: string;
  slug: string;
}
export interface CreateRecipeByUrl {
  url: string;
}
export interface CreateRecipeByUrlBulk {
  imports: CreateRecipeBulk[];
}
export interface DeleteRecipes {
  recipes: string[];
}
export interface ExportBase {
  recipes: string[];
}
export interface ExportRecipes {
  recipes: string[];
  exportType?: ExportTypes & string;
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
/**
 * A list of ingredient references.
 */
export interface IngredientReferences {
  referenceId?: string;
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
  id: string;
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
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  onHand?: boolean;
}
export interface RecipeStep {
  id?: string;
  title?: string;
  text: string;
  ingredientReferences?: IngredientReferences[];
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
export interface RecipeCommentCreate {
  recipeId: string;
  text: string;
}
export interface RecipeCommentSave {
  recipeId: string;
  text: string;
  userId: string;
}
export interface RecipeCommentUpdate {
  id: string;
  text: string;
}
export interface RecipeShareToken {
  recipeId: string;
  expiresAt?: string;
  groupId: string;
  id: string;
  createdAt: string;
  recipe: Recipe;
}
export interface RecipeShareTokenCreate {
  recipeId: string;
  expiresAt?: string;
}
export interface RecipeShareTokenSave {
  recipeId: string;
  expiresAt?: string;
  groupId: string;
}
export interface RecipeShareTokenSummary {
  recipeId: string;
  expiresAt?: string;
  groupId: string;
  id: string;
  createdAt: string;
}
export interface RecipeSlug {
  slug: string;
}
export interface RecipeTagResponse {
  name: string;
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeTool1 {
  name: string;
  onHand?: boolean;
  id: string;
  slug: string;
}
export interface RecipeToolCreate {
  name: string;
  onHand?: boolean;
}
export interface RecipeToolResponse {
  name: string;
  onHand?: boolean;
  id: string;
  slug: string;
  recipes?: Recipe[];
}
export interface RecipeToolSave {
  name: string;
  onHand?: boolean;
  groupId: string;
}
export interface SaveIngredientFood {
  name: string;
  description?: string;
  labelId?: string;
  groupId: string;
}
export interface SaveIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  groupId: string;
}
export interface SlugResponse {}
export interface TagIn {
  name: string;
}
export interface TagOut {
  name: string;
  groupId: string;
  id: string;
  slug: string;
}
export interface TagSave {
  name: string;
  groupId: string;
}
export interface UnitFoodBase {
  name: string;
  description?: string;
}
