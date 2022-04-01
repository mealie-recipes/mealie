/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type SupportedMigrations = "nextcloud" | "chowdown" | "paprika" | "mealie_alpha";

export interface CreateGroupPreferences {
  privateGroup?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
  groupId: string;
}
export interface CreateInviteToken {
  uses: number;
}
export interface CreateWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
}
export interface DataMigrationCreate {
  sourceType: SupportedMigrations;
}
export interface EmailInitationResponse {
  success: boolean;
  error?: string;
}
export interface EmailInvitation {
  email: string;
  token: string;
}
export interface GroupAdminUpdate {
  id: string;
  name: string;
  preferences: UpdateGroupPreferences;
}
export interface UpdateGroupPreferences {
  privateGroup?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
}
export interface GroupDataExport {
  id: string;
  groupId: string;
  name: string;
  filename: string;
  path: string;
  size: string;
  expires: string;
}
export interface GroupEventNotifierCreate {
  name: string;
  appriseUrl: string;
}
/**
 * These events are in-sync with the EventTypes found in the EventBusService.
 * If you modify this, make sure to update the EventBusService as well.
 */
export interface GroupEventNotifierOptions {
  recipeCreated?: boolean;
  recipeUpdated?: boolean;
  recipeDeleted?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  mealplanEntryCreated?: boolean;
  shoppingListCreated?: boolean;
  shoppingListUpdated?: boolean;
  shoppingListDeleted?: boolean;
  cookbookCreated?: boolean;
  cookbookUpdated?: boolean;
  cookbookDeleted?: boolean;
  tagCreated?: boolean;
  tagUpdated?: boolean;
  tagDeleted?: boolean;
  categoryCreated?: boolean;
  categoryUpdated?: boolean;
  categoryDeleted?: boolean;
}
/**
 * These events are in-sync with the EventTypes found in the EventBusService.
 * If you modify this, make sure to update the EventBusService as well.
 */
export interface GroupEventNotifierOptionsOut {
  recipeCreated?: boolean;
  recipeUpdated?: boolean;
  recipeDeleted?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  mealplanEntryCreated?: boolean;
  shoppingListCreated?: boolean;
  shoppingListUpdated?: boolean;
  shoppingListDeleted?: boolean;
  cookbookCreated?: boolean;
  cookbookUpdated?: boolean;
  cookbookDeleted?: boolean;
  tagCreated?: boolean;
  tagUpdated?: boolean;
  tagDeleted?: boolean;
  categoryCreated?: boolean;
  categoryUpdated?: boolean;
  categoryDeleted?: boolean;
  id: string;
}
/**
 * These events are in-sync with the EventTypes found in the EventBusService.
 * If you modify this, make sure to update the EventBusService as well.
 */
export interface GroupEventNotifierOptionsSave {
  recipeCreated?: boolean;
  recipeUpdated?: boolean;
  recipeDeleted?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  mealplanEntryCreated?: boolean;
  shoppingListCreated?: boolean;
  shoppingListUpdated?: boolean;
  shoppingListDeleted?: boolean;
  cookbookCreated?: boolean;
  cookbookUpdated?: boolean;
  cookbookDeleted?: boolean;
  tagCreated?: boolean;
  tagUpdated?: boolean;
  tagDeleted?: boolean;
  categoryCreated?: boolean;
  categoryUpdated?: boolean;
  categoryDeleted?: boolean;
  notifierId: string;
}
export interface GroupEventNotifierOut {
  id: string;
  name: string;
  enabled: boolean;
  groupId: string;
  options: GroupEventNotifierOptionsOut;
}
export interface GroupEventNotifierPrivate {
  id: string;
  name: string;
  enabled: boolean;
  groupId: string;
  options: GroupEventNotifierOptionsOut;
  appriseUrl: string;
}
export interface GroupEventNotifierSave {
  name: string;
  appriseUrl: string;
  enabled?: boolean;
  groupId: string;
  options?: GroupEventNotifierOptions;
}
export interface GroupEventNotifierUpdate {
  name: string;
  appriseUrl?: string;
  enabled?: boolean;
  groupId: string;
  options?: GroupEventNotifierOptions;
  id: string;
}
export interface GroupStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalCategories: number;
  totalTags: number;
  totalTools: number;
}
export interface GroupStorage {
  usedStorageBytes: number;
  usedStorageStr: string;
  totalStorageBytes: number;
  totalStorageStr: string;
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
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: string;
}
export interface ReadGroupPreferences {
  privateGroup?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
  groupId: string;
  id: string;
}
export interface ReadInviteToken {
  token: string;
  usesLeft: number;
  groupId: string;
}
export interface ReadWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
  groupId: string;
  id: string;
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
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: string;
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
  originalText?: string;
  referenceId?: string;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
  labelId?: string;
}
export interface SaveInviteToken {
  usesLeft: number;
  groupId: string;
  token: string;
}
export interface SaveWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
  groupId: string;
}
export interface SetPermissions {
  userId: string;
  canManage?: boolean;
  canInvite?: boolean;
  canOrganize?: boolean;
}
export interface ShoppingListCreate {
  name?: string;
}
export interface ShoppingListItemCreate {
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  isFood?: boolean;
  note?: string;
  quantity?: number;
  unitId?: string;
  unit?: IngredientUnit;
  foodId?: string;
  food?: IngredientFood;
  labelId?: string;
  recipeReferences?: ShoppingListItemRecipeRef[];
}
export interface ShoppingListItemRecipeRef {
  recipeId: string;
  recipeQuantity: number;
}
export interface ShoppingListItemOut {
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  isFood?: boolean;
  note?: string;
  quantity?: number;
  unitId?: string;
  unit?: IngredientUnit;
  foodId?: string;
  food?: IngredientFood;
  labelId?: string;
  recipeReferences?: ShoppingListItemRecipeRefOut[];
  id: string;
  label?: MultiPurposeLabelSummary;
}
export interface ShoppingListItemRecipeRefOut {
  recipeId: string;
  recipeQuantity: number;
  id: string;
  shoppingListItemId: string;
}
export interface ShoppingListItemUpdate {
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  isFood?: boolean;
  note?: string;
  quantity?: number;
  unitId?: string;
  unit?: IngredientUnit;
  foodId?: string;
  food?: IngredientFood;
  labelId?: string;
  recipeReferences?: ShoppingListItemRecipeRef[];
  id: string;
}
export interface ShoppingListOut {
  name?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
  recipeReferences: ShoppingListRecipeRefOut[];
}
export interface ShoppingListRecipeRefOut {
  id: string;
  shoppingListId: string;
  recipeId: string;
  recipeQuantity: number;
  recipe: RecipeSummary;
}
export interface ShoppingListSave {
  name?: string;
  groupId: string;
}
export interface ShoppingListSummary {
  name?: string;
  groupId: string;
  id: string;
}
export interface ShoppingListUpdate {
  name?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
}
