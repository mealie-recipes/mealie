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
export interface GroupEventNotifierOptions {
  recipeCreate?: boolean;
  recipeUpdate?: boolean;
  recipeDelete?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  newMealplanEntry?: boolean;
  shoppingListCreate?: boolean;
  shoppingListUpdate?: boolean;
  shoppingListDelete?: boolean;
  cookbookCreate?: boolean;
  cookbookUpdate?: boolean;
  cookbookDelete?: boolean;
  tagCreate?: boolean;
  tagUpdate?: boolean;
  tagDelete?: boolean;
  categoryCreate?: boolean;
  categoryUpdate?: boolean;
  categoryDelete?: boolean;
}
export interface GroupEventNotifierOptionsOut {
  recipeCreate?: boolean;
  recipeUpdate?: boolean;
  recipeDelete?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  newMealplanEntry?: boolean;
  shoppingListCreate?: boolean;
  shoppingListUpdate?: boolean;
  shoppingListDelete?: boolean;
  cookbookCreate?: boolean;
  cookbookUpdate?: boolean;
  cookbookDelete?: boolean;
  tagCreate?: boolean;
  tagUpdate?: boolean;
  tagDelete?: boolean;
  categoryCreate?: boolean;
  categoryUpdate?: boolean;
  categoryDelete?: boolean;
  id: string;
}
export interface GroupEventNotifierOptionsSave {
  recipeCreate?: boolean;
  recipeUpdate?: boolean;
  recipeDelete?: boolean;
  userSignup?: boolean;
  dataMigrations?: boolean;
  dataExport?: boolean;
  dataImport?: boolean;
  newMealplanEntry?: boolean;
  shoppingListCreate?: boolean;
  shoppingListUpdate?: boolean;
  shoppingListDelete?: boolean;
  cookbookCreate?: boolean;
  cookbookUpdate?: boolean;
  cookbookDelete?: boolean;
  tagCreate?: boolean;
  tagUpdate?: boolean;
  tagDelete?: boolean;
  categoryCreate?: boolean;
  categoryUpdate?: boolean;
  categoryDelete?: boolean;
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
export interface IngredientFood {
  name: string;
  description?: string;
  id: number;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: number;
}
export interface MultiPurposeLabelSummary {
  name: string;
  groupId: string;
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
  id: number;
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
  id: number;
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
/**
 * Create Shopping List
 */
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
  unitId?: number;
  unit?: IngredientUnit;
  foodId?: number;
  food?: IngredientFood;
  recipeId?: number;
  labelId?: string;
}
export interface ShoppingListItemOut {
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  isFood?: boolean;
  note?: string;
  quantity?: number;
  unitId?: number;
  unit?: IngredientUnit;
  foodId?: number;
  food?: IngredientFood;
  recipeId?: number;
  labelId?: string;
  id: string;
  label?: MultiPurposeLabelSummary;
}
/**
 * Create Shopping List
 */
export interface ShoppingListOut {
  name?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
}
/**
 * Create Shopping List
 */
export interface ShoppingListSave {
  name?: string;
  groupId: string;
}
/**
 * Create Shopping List
 */
export interface ShoppingListSummary {
  name?: string;
  groupId: string;
  id: string;
}
/**
 * Create Shopping List
 */
export interface ShoppingListUpdate {
  name?: string;
  groupId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
}
