/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ExportTypes = "json";
export type RegisteredParser = "nlp" | "brute" | "openai";
export type TimelineEventType = "system" | "info" | "comment";
export type TimelineEventImage = "has image" | "does not have image";

export interface AssignCategories {
  recipes: string[];
  categories: CategoryBase[];
}
export interface CategoryBase {
  name: string;
  id: string;
  slug: string;
}
export interface AssignSettings {
  recipes: string[];
  settings: RecipeSettings;
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
export interface AssignTags {
  recipes: string[];
  tags: TagBase[];
}
export interface TagBase {
  name: string;
  id: string;
  slug: string;
}
export interface CategoryIn {
  name: string;
}
export interface CategoryOut {
  name: string;
  id: string;
  slug: string;
  groupId: string;
}
export interface CategorySave {
  name: string;
  groupId: string;
}
export interface CreateIngredientFood {
  name: string;
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
  aliases?: CreateIngredientFoodAlias[];
  onHand?: boolean;
}
export interface CreateIngredientFoodAlias {
  name: string;
}
export interface CreateIngredientUnit {
  name: string;
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string;
  useAbbreviation?: boolean;
  aliases?: CreateIngredientUnitAlias[];
}
export interface CreateIngredientUnitAlias {
  name: string;
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
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: string;
  name: string;
  slug: string;
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
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
  aliases?: IngredientFoodAlias[];
  id: string;
  label?: MultiPurposeLabelSummary;
  createdAt?: string;
  updateAt?: string;
  onHand?: boolean;
}
export interface IngredientFoodAlias {
  name: string;
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
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string;
  useAbbreviation?: boolean;
  aliases?: IngredientUnitAlias[];
  id: string;
  createdAt?: string;
  updateAt?: string;
}
export interface IngredientUnitAlias {
  name: string;
}
export interface IngredientsRequest {
  parser?: RegisteredParser & string;
  ingredients: string[];
}
export interface MergeFood {
  fromFood: string;
  toFood: string;
}
export interface MergeUnit {
  fromUnit: string;
  toUnit: string;
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
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  title?: string;
  originalText?: string;
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
  dateAdded?: string;
  dateUpdated?: string;
  createdAt?: string;
  updateAt?: string;
  lastMade?: string;
  recipeIngredient?: RecipeIngredient[];
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
  id: string;
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
  dateAdded?: string;
  dateUpdated?: string;
  createdAt?: string;
  updateAt?: string;
  lastMade?: string;
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
export interface RecipeDuplicate {
  name?: string;
}
export interface RecipeIngredientBase {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
}
export interface RecipeLastMade {
  timestamp: string;
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
export interface RecipeTimelineEventCreate {
  recipeId: string;
  userId: string;
  subject: string;
  eventType: TimelineEventType;
  eventMessage?: string;
  image?: TimelineEventImage & string;
  timestamp?: string;
}
export interface RecipeTimelineEventIn {
  recipeId: string;
  userId?: string;
  subject: string;
  eventType: TimelineEventType;
  eventMessage?: string;
  image?: TimelineEventImage & string;
  timestamp?: string;
}
export interface RecipeTimelineEventOut {
  recipeId: string;
  userId: string;
  subject: string;
  eventType: TimelineEventType;
  eventMessage?: string;
  image?: TimelineEventImage & string;
  timestamp?: string;
  id: string;
  createdAt: string;
  updateAt: string;
}
export interface RecipeTimelineEventUpdate {
  subject: string;
  eventMessage?: string;
  image?: TimelineEventImage;
}
export interface RecipeToolCreate {
  name: string;
  onHand?: boolean;
}
export interface RecipeToolOut {
  name: string;
  onHand?: boolean;
  id: string;
  slug: string;
}
export interface RecipeToolResponse {
  name: string;
  onHand?: boolean;
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeToolSave {
  name: string;
  onHand?: boolean;
  groupId: string;
}
export interface RecipeZipTokenResponse {
  token: string;
}
export interface SaveIngredientFood {
  name: string;
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
  aliases?: CreateIngredientFoodAlias[];
  groupId: string;
}
export interface SaveIngredientUnit {
  name: string;
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string;
  useAbbreviation?: boolean;
  aliases?: CreateIngredientUnitAlias[];
  groupId: string;
}
export interface ScrapeRecipe {
  url: string;
  includeTags?: boolean;
}
export interface ScrapeRecipeTest {
  url: string;
}
export interface SlugResponse { }
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
  pluralName?: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
}
export interface UpdateImageResponse {
  image: string;
}
