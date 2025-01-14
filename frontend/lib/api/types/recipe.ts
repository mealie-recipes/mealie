/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ExportTypes = "json";
export type RegisteredParser = "nlp" | "brute" | "openai";
export type OrderByNullPosition = "first" | "last";
export type OrderDirection = "asc" | "desc";
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
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  labelId?: string | null;
  aliases?: CreateIngredientFoodAlias[];
  householdsWithIngredientFood?: string[];
}
export interface CreateIngredientFoodAlias {
  name: string;
}
export interface CreateIngredientUnit {
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string | null;
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
  categories?: RecipeCategory[] | null;
  tags?: RecipeTag[] | null;
}
export interface RecipeCategory {
  id?: string | null;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: string | null;
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
  exportType?: ExportTypes;
}
export interface IngredientConfidence {
  average?: number | null;
  comment?: number | null;
  name?: number | null;
  unit?: number | null;
  quantity?: number | null;
  food?: number | null;
}
export interface IngredientFood {
  id: string;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  labelId?: string | null;
  aliases?: IngredientFoodAlias[];
  householdsWithIngredientFood?: string[];
  label?: MultiPurposeLabelSummary | null;
  createdAt?: string | null;
  updatedAt?: string | null;
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
export interface IngredientReferences {
  referenceId?: string | null;
}
export interface IngredientRequest {
  parser?: RegisteredParser;
  ingredient: string;
}
export interface IngredientUnit {
  id: string;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string | null;
  useAbbreviation?: boolean;
  aliases?: IngredientUnitAlias[];
  createdAt?: string | null;
  updatedAt?: string | null;
}
export interface IngredientUnitAlias {
  name: string;
}
export interface IngredientsRequest {
  parser?: RegisteredParser;
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
  calories?: string | null;
  carbohydrateContent?: string | null;
  cholesterolContent?: string | null;
  fatContent?: string | null;
  fiberContent?: string | null;
  proteinContent?: string | null;
  saturatedFatContent?: string | null;
  sodiumContent?: string | null;
  sugarContent?: string | null;
  transFatContent?: string | null;
  unsaturatedFatContent?: string | null;
}
export interface ParsedIngredient {
  input?: string | null;
  confidence?: IngredientConfidence;
  ingredient: RecipeIngredient;
}
export interface RecipeIngredient {
  quantity?: number | null;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean | null;
  disableAmount?: boolean;
  display?: string;
  title?: string | null;
  originalText?: string | null;
  referenceId?: string;
}
export interface Recipe {
  id?: string | null;
  userId?: string;
  householdId?: string;
  groupId?: string;
  name?: string | null;
  slug?: string;
  image?: unknown;
  recipeServings?: number;
  recipeYieldQuantity?: number;
  recipeYield?: string | null;
  totalTime?: string | null;
  prepTime?: string | null;
  cookTime?: string | null;
  performTime?: string | null;
  description?: string | null;
  recipeCategory?: RecipeCategory[] | null;
  tags?: RecipeTag[] | null;
  tools?: RecipeTool[];
  rating?: number | null;
  orgURL?: string | null;
  dateAdded?: string | null;
  dateUpdated?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  lastMade?: string | null;
  recipeIngredient?: RecipeIngredient[];
  recipeInstructions?: RecipeStep[] | null;
  nutrition?: Nutrition | null;
  settings?: RecipeSettings | null;
  assets?: RecipeAsset[] | null;
  notes?: RecipeNote[] | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  comments?: RecipeCommentOut[] | null;
}
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  householdsWithTool?: string[];
}
export interface RecipeStep {
  id?: string | null;
  title?: string | null;
  summary?: string | null;
  text: string;
  ingredientReferences?: IngredientReferences[];
}
export interface RecipeAsset {
  name: string;
  icon: string;
  fileName?: string | null;
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
  updatedAt: string;
  userId: string;
  user: UserBase;
}
export interface UserBase {
  id: string;
  username?: string | null;
  admin: boolean;
}
export interface RecipeCategoryResponse {
  name: string;
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeSummary {
  id?: string | null;
  userId?: string;
  householdId?: string;
  groupId?: string;
  name?: string | null;
  slug?: string;
  image?: unknown;
  recipeServings?: number;
  recipeYieldQuantity?: number;
  recipeYield?: string | null;
  totalTime?: string | null;
  prepTime?: string | null;
  cookTime?: string | null;
  performTime?: string | null;
  description?: string | null;
  recipeCategory?: RecipeCategory[] | null;
  tags?: RecipeTag[] | null;
  tools?: RecipeTool[];
  rating?: number | null;
  orgURL?: string | null;
  dateAdded?: string | null;
  dateUpdated?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  lastMade?: string | null;
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
  name?: string | null;
}
export interface RecipeIngredientBase {
  quantity?: number | null;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean | null;
  disableAmount?: boolean | null;
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
export interface RecipeSuggestionQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
  limit?: number;
  maxMissingFoods?: number;
  maxMissingTools?: number;
  includeFoodsOnHand?: boolean;
  includeToolsOnHand?: boolean;
}
export interface RecipeSuggestionResponse {
  items: RecipeSuggestionResponseItem[];
}
export interface RecipeSuggestionResponseItem {
  recipe: RecipeSummary;
  missingFoods: IngredientFood[];
  missingTools: RecipeTool[];
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
  eventMessage?: string | null;
  image?: TimelineEventImage | null;
  timestamp?: string;
}
export interface RecipeTimelineEventIn {
  recipeId: string;
  userId?: string | null;
  subject: string;
  eventType: TimelineEventType;
  eventMessage?: string | null;
  image?: TimelineEventImage | null;
  timestamp?: string;
}
export interface RecipeTimelineEventOut {
  recipeId: string;
  userId: string;
  subject: string;
  eventType: TimelineEventType;
  eventMessage?: string | null;
  image?: TimelineEventImage | null;
  timestamp?: string;
  id: string;
  groupId: string;
  householdId: string;
  createdAt: string;
  updatedAt: string;
}
export interface RecipeTimelineEventUpdate {
  subject: string;
  eventMessage?: string | null;
  image?: TimelineEventImage | null;
}
export interface RecipeToolCreate {
  name: string;
  householdsWithTool?: string[];
}
export interface RecipeToolOut {
  name: string;
  householdsWithTool?: string[];
  id: string;
  slug: string;
}
export interface RecipeToolResponse {
  name: string;
  householdsWithTool?: string[];
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeToolSave {
  name: string;
  householdsWithTool?: string[];
  groupId: string;
}
export interface RecipeZipTokenResponse {
  token: string;
}
export interface SaveIngredientFood {
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  labelId?: string | null;
  aliases?: CreateIngredientFoodAlias[];
  householdsWithIngredientFood?: string[];
  groupId: string;
}
export interface SaveIngredientUnit {
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  fraction?: boolean;
  abbreviation?: string;
  pluralAbbreviation?: string | null;
  useAbbreviation?: boolean;
  aliases?: CreateIngredientUnitAlias[];
  groupId: string;
}
export interface ScrapeRecipe {
  includeTags?: boolean;
  url: string;
}
export interface ScrapeRecipeBase {
  includeTags?: boolean;
}
export interface ScrapeRecipeData {
  includeTags?: boolean;
  data: string;
}
export interface ScrapeRecipeTest {
  url: string;
  useOpenAI?: boolean;
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
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
}
export interface UpdateImageResponse {
  image: string;
}
export interface RequestQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
}
