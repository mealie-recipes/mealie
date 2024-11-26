/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type GroupRecipeActionType = "link" | "post";
export type WebhookType = "mealplan";

export interface CreateGroupRecipeAction {
  actionType: GroupRecipeActionType;
  title: string;
  url: string;
}
export interface CreateHouseholdPreferences {
  privateHousehold?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
}
export interface CreateInviteToken {
  uses: number;
  groupId?: string | null;
  householdId?: string | null;
}
export interface CreateWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
}
export interface EmailInitationResponse {
  success: boolean;
  error?: string | null;
}
export interface EmailInvitation {
  email: string;
  token: string;
}
export interface GroupEventNotifierCreate {
  name: string;
  appriseUrl?: string | null;
}
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
  householdId: string;
  options: GroupEventNotifierOptionsOut;
}
export interface GroupEventNotifierPrivate {
  id: string;
  name: string;
  enabled: boolean;
  groupId: string;
  householdId: string;
  options: GroupEventNotifierOptionsOut;
  appriseUrl: string;
}
export interface GroupEventNotifierSave {
  name: string;
  appriseUrl?: string | null;
  enabled?: boolean;
  groupId: string;
  householdId: string;
  options?: GroupEventNotifierOptions;
}
export interface GroupEventNotifierUpdate {
  name: string;
  appriseUrl?: string | null;
  enabled?: boolean;
  groupId: string;
  householdId: string;
  options?: GroupEventNotifierOptions;
  id: string;
}
export interface GroupRecipeActionOut {
  actionType: GroupRecipeActionType;
  title: string;
  url: string;
  groupId: string;
  householdId: string;
  id: string;
}
export interface GroupRecipeActionPayload {
  action: GroupRecipeActionOut;
  content: unknown;
}
export interface HouseholdCreate {
  groupId?: string | null;
  name: string;
}
export interface HouseholdInDB {
  groupId: string;
  name: string;
  id: string;
  slug: string;
  preferences?: ReadHouseholdPreferences | null;
  group: string;
  users?: HouseholdUserSummary[] | null;
  webhooks?: ReadWebhook[];
}
export interface ReadHouseholdPreferences {
  privateHousehold?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
  id: string;
}
export interface HouseholdUserSummary {
  id: string;
  fullName: string;
}
export interface ReadWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
  groupId: string;
  householdId: string;
  id: string;
}
export interface HouseholdRecipeBase {
  lastMade?: string | null;
}
export interface HouseholdRecipeCreate {
  lastMade?: string | null;
  householdId: string;
  recipeId: string;
}
export interface HouseholdRecipeOut {
  lastMade?: string | null;
  householdId: string;
  recipeId: string;
  id: string;
}
export interface HouseholdRecipeSummary {
  lastMade?: string | null;
  recipeId: string;
}
export interface HouseholdRecipeUpdate {
  lastMade?: string | null;
}
export interface HouseholdSave {
  groupId: string;
  name: string;
}
export interface HouseholdStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalCategories: number;
  totalTags: number;
  totalTools: number;
}
export interface HouseholdSummary {
  groupId: string;
  name: string;
  id: string;
  slug: string;
  preferences?: ReadHouseholdPreferences | null;
}
export interface ReadInviteToken {
  token: string;
  usesLeft: number;
  groupId: string;
  householdId: string;
}
export interface SaveGroupRecipeAction {
  actionType: GroupRecipeActionType;
  title: string;
  url: string;
  groupId: string;
  householdId: string;
}
export interface SaveHouseholdPreferences {
  privateHousehold?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
  householdId: string;
}
export interface SaveInviteToken {
  usesLeft: number;
  groupId: string;
  householdId: string;
  token: string;
}
export interface SaveWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
  groupId: string;
  householdId: string;
}
export interface SetPermissions {
  userId: string;
  canManageHousehold?: boolean;
  canManage?: boolean;
  canInvite?: boolean;
  canOrganize?: boolean;
}
export interface ShoppingListAddRecipeParams {
  recipeIncrementQuantity?: number;
  recipeIngredients?: RecipeIngredient[] | null;
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
  [k: string]: unknown;
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
  [k: string]: unknown;
}
export interface CreateIngredientUnitAlias {
  name: string;
  [k: string]: unknown;
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
  [k: string]: unknown;
}
export interface MultiPurposeLabelSummary {
  name: string;
  color?: string;
  groupId: string;
  id: string;
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
  [k: string]: unknown;
}
export interface CreateIngredientFoodAlias {
  name: string;
  [k: string]: unknown;
}
export interface ShoppingListCreate {
  name?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  createdAt?: string | null;
  updatedAt?: string | null;
}
export interface ShoppingListItemBase {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean;
  disableAmount?: boolean | null;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string | null;
  labelId?: string | null;
  unitId?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
}
export interface ShoppingListItemCreate {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean;
  disableAmount?: boolean | null;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string | null;
  labelId?: string | null;
  unitId?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  id?: string | null;
  recipeReferences?: ShoppingListItemRecipeRefCreate[];
}
export interface ShoppingListItemRecipeRefCreate {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number | null;
  recipeNote?: string | null;
}
export interface ShoppingListItemOut {
  quantity?: number;
  unit?: IngredientUnit | null;
  food?: IngredientFood | null;
  note?: string | null;
  isFood?: boolean;
  disableAmount?: boolean | null;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string | null;
  labelId?: string | null;
  unitId?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  id: string;
  groupId: string;
  householdId: string;
  label?: MultiPurposeLabelSummary | null;
  recipeReferences?: ShoppingListItemRecipeRefOut[];
  createdAt?: string | null;
  updatedAt?: string | null;
}
export interface ShoppingListItemRecipeRefOut {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number | null;
  recipeNote?: string | null;
  id: string;
  shoppingListItemId: string;
}
export interface ShoppingListItemRecipeRefUpdate {
  recipeId: string;
  recipeQuantity?: number;
  recipeScale?: number | null;
  recipeNote?: string | null;
  id: string;
  shoppingListItemId: string;
}
export interface ShoppingListItemUpdate {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean;
  disableAmount?: boolean | null;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string | null;
  labelId?: string | null;
  unitId?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  recipeReferences?: (ShoppingListItemRecipeRefCreate | ShoppingListItemRecipeRefUpdate)[];
}
export interface ShoppingListItemUpdateBulk {
  quantity?: number;
  unit?: IngredientUnit | CreateIngredientUnit | null;
  food?: IngredientFood | CreateIngredientFood | null;
  note?: string | null;
  isFood?: boolean;
  disableAmount?: boolean | null;
  display?: string;
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  foodId?: string | null;
  labelId?: string | null;
  unitId?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  recipeReferences?: (ShoppingListItemRecipeRefCreate | ShoppingListItemRecipeRefUpdate)[];
  id: string;
}
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
  name?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  groupId: string;
  userId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
  householdId: string;
  recipeReferences?: ShoppingListRecipeRefOut[];
  labelSettings?: ShoppingListMultiPurposeLabelOut[];
}
export interface ShoppingListRecipeRefOut {
  id: string;
  shoppingListId: string;
  recipeId: string;
  recipeQuantity: number;
  recipe: RecipeSummary;
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
export interface RecipeCategory {
  id?: string | null;
  name: string;
  slug: string;
  [k: string]: unknown;
}
export interface RecipeTag {
  id?: string | null;
  name: string;
  slug: string;
  [k: string]: unknown;
}
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  householdsWithTool?: string[];
  [k: string]: unknown;
}
export interface ShoppingListRemoveRecipeParams {
  recipeDecrementQuantity?: number;
}
export interface ShoppingListSave {
  name?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  groupId: string;
  userId: string;
}
export interface ShoppingListSummary {
  name?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  groupId: string;
  userId: string;
  id: string;
  householdId: string;
  recipeReferences: ShoppingListRecipeRefOut[];
  labelSettings: ShoppingListMultiPurposeLabelOut[];
}
export interface ShoppingListUpdate {
  name?: string | null;
  extras?: {
    [k: string]: unknown;
  } | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  groupId: string;
  userId: string;
  id: string;
  listItems?: ShoppingListItemOut[];
}
export interface UpdateHousehold {
  groupId: string;
  name: string;
  id: string;
  slug: string;
}
export interface UpdateHouseholdAdmin {
  groupId: string;
  name: string;
  id: string;
  preferences?: UpdateHouseholdPreferences | null;
}
export interface UpdateHouseholdPreferences {
  privateHousehold?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  recipeDisableAmount?: boolean;
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
