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
  categories: CategoryDraft[];
}
export interface CategoryDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
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
  locked?: boolean;
}
export interface AssignTags {
  recipes: string[];
  tags: TagDraft[];
}
export interface TagDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
}
export interface CategoryCreate {
  name: string;
}
export interface CategoryOut {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
}
export interface CategorySave {
  name: string;
  groupId: string;
}
export interface CategoryWithRecipes {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
  recipes: RecipeSummary[];
}
export interface RecipeSummary {
  id: string;
  userId: string;
  householdId: string;
  groupId: string;
  name: string;
  slug: string;
  image: string | null;
  recipeServings: number;
  recipeYieldQuantity: number;
  recipeYield: string | null;
  totalTime: string | null;
  prepTime: string | null;
  performTime: string | null;
  totalTimeSeconds: number | null;
  prepTimeSeconds: number | null;
  performTimeSeconds: number | null;
  description: string | null;
  recipeCategory: CategoryOut[];
  tags: TagOut[];
  tools: ToolOut[];
  rating: number | null;
  orgURL: string | null;
  dateAdded: string | null;
  dateUpdated: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}
export interface TagOut {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
}
export interface ToolOut {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
  householdsWithTool: string[];
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
export interface IngredientFoodAlias {
  name: string;
}
export interface IngredientFoodAliasCreate {
  name: string;
}
export interface IngredientFoodCreate {
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  labelId?: string | null;
  aliases?: IngredientFoodAliasCreate[];
  substitutions?: IngredientFoodSubstitutionCreate[];
  householdsWithIngredientFood?: string[];
}
export interface IngredientFoodSubstitutionCreate {
  substituteFoodId?: string | null;
  note?: string | null;
}
export interface IngredientFoodMerge {
  fromFood: string;
  toFood: string;
}
export interface IngredientFoodOut {
  id: string;
  name: string;
  pluralName: string | null;
  description: string;
  extras: {
    [k: string]: unknown;
  } | null;
  labelId: string | null;
  aliases: IngredientFoodAlias[];
  substitutions: IngredientFoodSubstitution[];
  householdsWithIngredientFood: string[];
  label: MultiPurposeLabelSummary | null;
  recipeCount: number;
  createdAt: string | null;
  updatedAt: string | null;
}
export interface IngredientFoodSubstitution {
  substituteFoodId?: string | null;
  note?: string | null;
  substituteFood?: IngredientFoodSummary | null;
}
export interface IngredientFoodSummary {
  id: string;
  name: string;
  pluralName: string | null;
}
export interface MultiPurposeLabelSummary {
  name: string;
  color: string;
  groupId: string;
  id: string;
}
export interface IngredientFoodSave {
  id?: string | null;
  name: string;
  pluralName?: string | null;
  description?: string;
  extras?: {
    [k: string]: unknown;
  } | null;
  labelId?: string | null;
  aliases?: IngredientFoodAliasCreate[];
  substitutions?: IngredientFoodSubstitutionCreate[];
  householdsWithIngredientFood?: string[];
  groupId: string;
}
export interface IngredientReferences {
  referenceId?: string | null;
}
export interface IngredientRequest {
  parser?: RegisteredParser;
  ingredient: string;
}
export interface IngredientUnitAlias {
  name: string;
}
export interface IngredientUnitAliasCreate {
  name: string;
}
export interface IngredientUnitCreate {
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
  aliases?: IngredientUnitAliasCreate[];
  standardQuantity?: number | null;
  standardUnit?: string | null;
}
export interface IngredientUnitMerge {
  fromUnit: string;
  toUnit: string;
}
export interface IngredientUnitOut {
  id: string;
  name: string;
  pluralName: string | null;
  description: string;
  extras: {
    [k: string]: unknown;
  } | null;
  fraction: boolean;
  abbreviation: string;
  pluralAbbreviation: string | null;
  useAbbreviation: boolean;
  aliases: IngredientUnitAlias[];
  standardQuantity: number | null;
  standardUnit: string | null;
  createdAt: string | null;
  updatedAt: string | null;
}
export interface IngredientUnitSave {
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
  aliases?: IngredientUnitAliasCreate[];
  standardQuantity?: number | null;
  standardUnit?: string | null;
  groupId: string;
}
export interface IngredientsRequest {
  parser?: RegisteredParser;
  ingredients: string[];
}
export interface NoteReference {
  referenceId?: string | null;
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
export interface OrganizerDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
}
export interface OrganizerMerge {
  fromId: string;
  toId: string;
}
export interface OrganizerOut {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
}
export interface ParsedIngredient {
  input?: string | null;
  confidence?: IngredientConfidence;
  ingredient: RecipeIngredient;
}
export interface RecipeIngredient {
  quantity?: number | null;
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
  display?: string;
  title?: string | null;
  originalText?: string | null;
  substitutions?: RecipeIngredientSubstitution[];
  referenceId?: string;
}
export interface RecipeDraft {
  id?: string | null;
  userId?: string | null;
  householdId?: string | null;
  groupId?: string | null;
  name?: string | null;
  slug?: string;
  image?: unknown;
  recipeServings?: number;
  recipeYieldQuantity?: number;
  recipeYield?: string | null;
  totalTime?: string | null;
  prepTime?: string | null;
  performTime?: string | null;
  totalTimeSeconds?: number | null;
  prepTimeSeconds?: number | null;
  performTimeSeconds?: number | null;
  description?: string | null;
  recipeCategory?: CategoryDraft[];
  tags?: TagDraft[];
  tools?: ToolDraft[];
  rating?: number | null;
  orgURL?: string | null;
  dateAdded?: string | null;
  dateUpdated?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  recipeIngredient?: RecipeIngredient[];
  recipeInstructions?: RecipeStep[];
  nutrition?: Nutrition | null;
  settings?: RecipeSettings | null;
  assets?: RecipeAsset[];
  notes?: RecipeNote[];
  extras?: {
    [k: string]: unknown;
  };
  comments?: RecipeCommentOut[];
}
export interface ToolDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
  householdsWithTool?: string[];
}
export interface RecipeStep {
  id?: string | null;
  title?: string | null;
  summary?: string | null;
  text: string;
  ingredientReferences?: IngredientReferences[];
  noteReferences?: NoteReference[];
  durationSeconds?: number | null;
}
export interface RecipeAsset {
  name: string;
  icon: string;
  fileName?: string | null;
}
export interface RecipeNote {
  title: string;
  text: string;
  referenceId?: string;
}
export interface RecipeCommentOut {
  id: string;
  recipeId: string;
  text: string;
  createdAt: string;
  updatedAt: string;
  userId: string;
  user: RecipeCommentUser;
}
export interface RecipeCommentUser {
  id: string;
  username?: string | null;
  admin: boolean;
  fullName?: string | null;
}
export interface RecipeIngredientSubstitution {
  substituteFoodId?: string | null;
  note?: string | null;
  substituteFood?: IngredientFoodSummary | null;
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
export interface RecipeCreate {
  name: string;
}
export interface RecipeDuplicate {
  name?: string | null;
}
export interface RecipeIngredientBase {
  quantity?: number | null;
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
  display?: string;
}
export interface RecipeIngredientSubstitutionCreate {
  substituteFoodId?: string | null;
  note?: string | null;
}
export interface RecipeLastMade {
  timestamp: string;
}
export interface RecipeOut {
  id: string;
  userId: string;
  householdId: string;
  groupId: string;
  name: string;
  slug: string;
  image: string | null;
  recipeServings: number;
  recipeYieldQuantity: number;
  recipeYield: string | null;
  totalTime: string | null;
  prepTime: string | null;
  performTime: string | null;
  totalTimeSeconds: number | null;
  prepTimeSeconds: number | null;
  performTimeSeconds: number | null;
  description: string | null;
  recipeCategory: CategoryOut[];
  tags: TagOut[];
  tools: ToolOut[];
  rating: number | null;
  orgURL: string | null;
  dateAdded: string | null;
  dateUpdated: string | null;
  createdAt: string | null;
  updatedAt: string | null;
  recipeIngredient: RecipeIngredient[];
  recipeInstructions: RecipeStep[];
  nutrition: Nutrition;
  settings: RecipeSettings;
  assets: RecipeAsset[];
  notes: RecipeNote[];
  extras: {
    [k: string]: unknown;
  };
  comments: RecipeCommentOut[];
}
export interface RecipeShareTokenCreate {
  recipeId: string;
  expiresAt?: string;
}
export interface RecipeShareTokenOut {
  recipeId: string;
  expiresAt: string;
  groupId: string;
  id: string;
  createdAt: string;
  recipe: RecipeOut;
}
export interface RecipeShareTokenSave {
  recipeId: string;
  expiresAt?: string;
  groupId: string;
}
export interface RecipeShareTokenSummary {
  recipeId: string;
  expiresAt: string;
  groupId: string;
  id: string;
  createdAt: string;
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
  includeSubstitutions?: boolean;
}
export interface RecipeSuggestionResponse {
  items: RecipeSuggestionResponseItem[];
}
export interface RecipeSuggestionResponseItem {
  recipe: RecipeSummary;
  missingFoods: IngredientFoodOut[];
  substitutedFoods: RecipeSuggestionSubstitutedFood[];
  missingTools: ToolOut[];
}
export interface RecipeSuggestionSubstitutedFood {
  food: IngredientFoodOut;
  substituteFood: IngredientFoodSummary;
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
  eventMessage: string | null;
  image: TimelineEventImage | null;
  timestamp: string;
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
export interface RecipeUrlBulkCreate {
  imports: RecipeUrlCreate[];
}
export interface RecipeUrlCreate {
  url: string;
  categories?: CategoryDraft[] | null;
  tags?: TagDraft[] | null;
}
export interface ScrapeRecipe {
  includeTags?: boolean;
  includeCategories?: boolean;
  url: string;
}
export interface ScrapeRecipeAI {
  content?: string | null;
  url?: string | null;
  translateLanguage?: string | null;
  createNewOrganizers?: boolean;
}
export interface ScrapeRecipeBase {
  includeTags?: boolean;
  includeCategories?: boolean;
}
export interface ScrapeRecipeData {
  includeTags?: boolean;
  includeCategories?: boolean;
  data: string;
  url?: string | null;
}
export interface ScrapeRecipeTest {
  url: string;
  useOpenAI?: boolean;
}
export interface SubstitutionBase {
  substituteFoodId?: string | null;
  note?: string | null;
}
export interface TagCreate {
  name: string;
}
export interface TagSave {
  name: string;
  groupId: string;
}
export interface TagWithRecipes {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
  recipes: RecipeSummary[];
}
export interface ToolCreate {
  name: string;
  householdsWithTool?: string[];
}
export interface ToolSave {
  name: string;
  householdsWithTool?: string[];
  groupId: string;
}
export interface ToolWithRecipes {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
  householdsWithTool: string[];
  recipes: RecipeSummary[];
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
export interface MealieOutModel {}
export interface RequestQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
}
