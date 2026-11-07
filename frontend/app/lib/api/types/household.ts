/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type GroupRecipeActionType = "link" | "post";
export type WebhookType = "mealplan";

export interface EmailInvitation {
  email: string;
  token: string;
}
export interface EmailInvitationResponse {
  success: boolean;
  error?: string | null;
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
  mealplanEntryUpdated?: boolean;
  mealplanEntryDeleted?: boolean;
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
  labelCreated?: boolean;
  labelUpdated?: boolean;
  labelDeleted?: boolean;
}
export interface GroupEventNotifierOptionsOut {
  testMessage: boolean;
  webhookTask: boolean;
  recipeCreated: boolean;
  recipeUpdated: boolean;
  recipeDeleted: boolean;
  userSignup: boolean;
  dataMigrations: boolean;
  dataExport: boolean;
  dataImport: boolean;
  mealplanEntryCreated: boolean;
  mealplanEntryUpdated: boolean;
  mealplanEntryDeleted: boolean;
  shoppingListCreated: boolean;
  shoppingListUpdated: boolean;
  shoppingListDeleted: boolean;
  cookbookCreated: boolean;
  cookbookUpdated: boolean;
  cookbookDeleted: boolean;
  tagCreated: boolean;
  tagUpdated: boolean;
  tagDeleted: boolean;
  categoryCreated: boolean;
  categoryUpdated: boolean;
  categoryDeleted: boolean;
  labelCreated: boolean;
  labelUpdated: boolean;
  labelDeleted: boolean;
  id: string;
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
export interface GroupRecipeActionCreate {
  actionType: GroupRecipeActionType;
  title: string;
  url: string;
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
  recipeScale: number;
}
export interface GroupRecipeActionSave {
  actionType: GroupRecipeActionType;
  title: string;
  url: string;
  groupId: string;
  householdId: string;
}
export interface HouseholdAdminUpdate {
  groupId: string;
  name: string;
  id: string;
  preferences?: HouseholdPreferencesUpdate | null;
}
export interface HouseholdPreferencesUpdate {
  privateHousehold?: boolean;
  showAnnouncements?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
}
export interface HouseholdCreate {
  groupId?: string | null;
  name: string;
}
export interface HouseholdOut {
  groupId: string;
  name: string;
  id: string;
  slug: string;
  preferences: HouseholdPreferencesOut | null;
  group: string;
  users: HouseholdUserSummary[] | null;
  webhooks: WebhookOut[];
}
export interface HouseholdPreferencesOut {
  privateHousehold: boolean;
  showAnnouncements: boolean;
  lockRecipeEditsFromOtherHouseholds: boolean;
  firstDayOfWeek: number;
  recipePublic: boolean;
  recipeShowNutrition: boolean;
  recipeShowAssets: boolean;
  recipeLandscapeView: boolean;
  recipeDisableComments: boolean;
  id: string;
}
export interface HouseholdUserSummary {
  id: string;
  fullName: string;
}
export interface WebhookOut {
  enabled: boolean;
  name: string;
  url: string;
  webhookType: WebhookType;
  scheduledTime: string;
  groupId: string;
  householdId: string;
  id: string;
}
export interface HouseholdPreferencesCreate {
  privateHousehold?: boolean;
  showAnnouncements?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
}
export interface HouseholdPreferencesSave {
  privateHousehold?: boolean;
  showAnnouncements?: boolean;
  lockRecipeEditsFromOtherHouseholds?: boolean;
  firstDayOfWeek?: number;
  recipePublic?: boolean;
  recipeShowNutrition?: boolean;
  recipeShowAssets?: boolean;
  recipeLandscapeView?: boolean;
  recipeDisableComments?: boolean;
  householdId: string;
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
  lastMade: string | null;
  householdId: string;
  recipeId: string;
  id: string;
}
export interface HouseholdRecipeSummary {
  lastMade: string | null;
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
  preferences: HouseholdPreferencesOut | null;
}
export interface HouseholdUpdate {
  groupId: string;
  name: string;
  id: string;
  slug: string;
}
export interface InviteTokenCreate {
  uses: number;
  groupId?: string | null;
  householdId?: string | null;
}
export interface InviteTokenOut {
  token: string;
  usesLeft: number;
  groupId: string;
  householdId: string;
}
export interface InviteTokenSave {
  usesLeft: number;
  groupId: string;
  householdId: string;
  token: string;
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
export interface IngredientUnitAlias {
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
export interface IngredientUnitAliasCreate {
  name: string;
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
export interface IngredientFoodAlias {
  name: string;
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
export interface IngredientFoodAliasCreate {
  name: string;
}
export interface IngredientFoodSubstitutionCreate {
  substituteFoodId?: string | null;
  note?: string | null;
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
export interface CategoryDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
}
export interface TagDraft {
  id?: string | null;
  groupId?: string | null;
  name: string;
  slug?: string | null;
  recipeCount?: number;
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
export interface IngredientReferences {
  referenceId?: string | null;
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
export interface RecipeSettings {
  public?: boolean;
  showNutrition?: boolean;
  showAssets?: boolean;
  landscapeView?: boolean;
  disableComments?: boolean;
  locked?: boolean;
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
export interface ShoppingListAddRecipeParamsBulk {
  recipeIncrementQuantity?: number;
  recipeIngredients?: RecipeIngredient[] | null;
  recipeId: string;
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
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
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
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
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
  quantity: number;
  unit: IngredientUnitOut | null;
  food: IngredientFoodOut | null;
  referencedRecipe: RecipeDraft | null;
  note: string | null;
  display: string;
  shoppingListId: string;
  checked: boolean;
  position: number;
  foodId: string | null;
  labelId: string | null;
  unitId: string | null;
  extras: {
    [k: string]: unknown;
  } | null;
  id: string;
  groupId: string;
  householdId: string;
  label: MultiPurposeLabelSummary | null;
  recipeReferences: ShoppingListItemRecipeRefOut[];
  createdAt: string | null;
  updatedAt: string | null;
}
export interface ShoppingListItemRecipeRefOut {
  recipeId: string;
  recipeQuantity: number;
  recipeScale: number | null;
  recipeNote: string | null;
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
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
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
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
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
  createdItems: ShoppingListItemOut[];
  updatedItems: ShoppingListItemOut[];
  deletedItems: ShoppingListItemOut[];
}
export interface ShoppingListMultiPurposeLabelCreate {
  shoppingListId: string;
  labelId: string;
  position?: number;
}
export interface ShoppingListMultiPurposeLabelOut {
  shoppingListId: string;
  labelId: string;
  position: number;
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
  name: string | null;
  extras: {
    [k: string]: unknown;
  } | null;
  createdAt: string | null;
  updatedAt: string | null;
  groupId: string;
  userId: string;
  id: string;
  listItems: ShoppingListItemOut[];
  householdId: string;
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
export interface CategoryOut {
  id: string;
  groupId: string;
  name: string;
  slug: string;
  recipeCount: number;
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
  name: string | null;
  extras: {
    [k: string]: unknown;
  } | null;
  createdAt: string | null;
  updatedAt: string | null;
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
export interface WebhookCreate {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
}
export interface WebhookSave {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
  groupId: string;
  householdId: string;
}
export interface MealieOutModel {}
export interface RecipeIngredientBase {
  quantity?: number | null;
  unit?: IngredientUnitOut | IngredientUnitCreate | null;
  food?: IngredientFoodOut | IngredientFoodCreate | null;
  referencedRecipe?: RecipeDraft | null;
  note?: string | null;
  display?: string;
}
