/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type WebhookType = "mealplan";
export type SupportedMigrations = "nextcloud" | "chowdown" | "copymethat" | "paprika" | "mealie_alpha" | "tandoor";

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
  webhookType?: WebhookType & string;
  scheduledTime: string;
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
  preferences?: UpdateGroupPreferences;
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
  testMessage?: boolean;
  webhookTask?: boolean;
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
  testMessage?: boolean;
  webhookTask?: boolean;
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
  testMessage?: boolean;
  webhookTask?: boolean;
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
  webhookType?: WebhookType & string;
  scheduledTime: string;
  groupId: string;
  id: string;
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
  webhookType?: WebhookType & string;
  scheduledTime: string;
  groupId: string;
}
export interface SeederConfig {
  locale: string;
}
export interface SetPermissions {
  userId: string;
  canManage?: boolean;
  canInvite?: boolean;
  canOrganize?: boolean;
}
export interface ShoppingListAddRecipeParams {
  recipeIncrementQuantity?: number;
  recipeIngredients?: RecipeIngredient[];
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
export interface IngredientUnit {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  useAbbreviation?: boolean;
  id: string;
  createdAt?: string;
  updateAt?: string;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  useAbbreviation?: boolean;
}
export interface IngredientFood {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
  id: string;
  label?: MultiPurposeLabelSummary;
  createdAt?: string;
  updateAt?: string;
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
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
}
export interface ShoppingListCreate {
  name?: string;
  extras?: {
    [k: string]: unknown;
  };
  createdAt?: string;
  updateAt?: string;
}
export interface ShoppingListItemBase {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string;
  labelId?: string;
  unitId?: string;
  extras?: {
    [k: string]: unknown;
  };
}
export interface ShoppingListItemCreate {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string;
  labelId?: string;
  unitId?: string;
  extras?: {
    [k: string]: unknown;
  };
  recipeReferences?: ShoppingListItemRecipeRefCreate[];
}
export interface ShoppingListItemRecipeRefCreate {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number;
}
export interface ShoppingListItemOut {
  quantity?: number;
  unit?: IngredientUnit;
  food?: IngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string;
  labelId?: string;
  unitId?: string;
  extras?: {
    [k: string]: unknown;
  };
  id: string;
  label?: MultiPurposeLabelSummary;
  recipeReferences?: ShoppingListItemRecipeRefOut[];
  createdAt?: string;
  updateAt?: string;
}
export interface ShoppingListItemRecipeRefOut {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number;
  id: string;
  shoppingListItemId: string;
}
export interface ShoppingListItemRecipeRefUpdate {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number;
  id: string;
  shoppingListItemId: string;
}
export interface ShoppingListItemUpdate {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string;
  labelId?: string;
  unitId?: string;
  extras?: {
    [k: string]: unknown;
  };
  recipeReferences?: (ShoppingListItemRecipeRefCreate | ShoppingListItemRecipeRefUpdate)[];
}
/**
 * Only used for bulk update operations where the shopping list item id isn't already supplied
 */
export interface ShoppingListItemUpdateBulk {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  note?: string;
  isFood?: boolean;
  disableAmount?: boolean;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string;
  labelId?: string;
  unitId?: string;
  extras?: {
    [k: string]: unknown;
  };
  recipeReferences?: (ShoppingListItemRecipeRefCreate | ShoppingListItemRecipeRefUpdate)[];
  id: string;
}
/**
 * Container for bulk shopping list item changes
 */
export interface ShoppingListItemsCollectionOut {
  createdItems?: ShoppingListItemOut[];
  updatedItems?: ShoppingListItemOut[];
  deletedItems?: ShoppingListItemOut[];
}
export interface ShoppingListMultiPurposeLabelCreate {
  shoppingListId: string;
  labelId: string;
  position?: number;
}
export interface ShoppingListMultiPurposeLabelOut {
  shoppingListId: string;
  labelId: string;
  position?: number;
  id: string;
  label: MultiPurposeLabelSummary;
}
export interface ShoppingListMultiPurposeLabelUpdate {
  shoppingListId: string;
  labelId: string;
  position?: number;
  id: string;
}
export interface ShoppingListOut {
  name?: string;
  extras?: {
    [k: string]: unknown;
  };
  createdAt?: string;
  updateAt?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
  recipeReferences: ShoppingListRecipeRefOut[];
  labelSettings: ShoppingListMultiPurposeLabelOut[];
}
export interface ShoppingListRecipeRefOut {
  id: string;
  shoppingListId: string;
  recipeId: string;
  recipeQuantity: number;
  recipe: RecipeSummary;
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
export interface ShoppingListRemoveRecipeParams {
  recipeDecrementQuantity?: number;
}
export interface ShoppingListSave {
  name?: string;
  extras?: {
    [k: string]: unknown;
  };
  createdAt?: string;
  updateAt?: string;
  groupId: string;
}
export interface ShoppingListSummary {
  name?: string;
  extras?: {
    [k: string]: unknown;
  };
  createdAt?: string;
  updateAt?: string;
  groupId: string;
  id: string;
  recipeReferences: ShoppingListRecipeRefOut[];
  labelSettings: ShoppingListMultiPurposeLabelOut[];
}
export interface ShoppingListUpdate {
  name?: string;
  extras?: {
    [k: string]: unknown;
  };
  createdAt?: string;
  updateAt?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
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
