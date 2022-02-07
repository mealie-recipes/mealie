/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CategoryBase {
  name: string;
  id: number;
  slug: string;
}
export interface ChangePassword {
  currentPassword: string;
  newPassword: string;
}
export interface CreateToken {
  name: string;
  userId: string;
  token: string;
}
export interface CreateUserRegistration {
  group?: string;
  groupToken?: string;
  email: string;
  username: string;
  password: string;
  passwordConfirm: string;
  advanced?: boolean;
  private?: boolean;
}
export interface ForgotPassword {
  email: string;
}
export interface GroupBase {
  name: string;
}
export interface GroupInDB {
  name: string;
  id: string;
  categories?: CategoryBase[];
  webhooks?: unknown[];
  users?: UserOut[];
  preferences?: ReadGroupPreferences;
}
export interface UserOut {
  username?: string;
  fullName?: string;
  email: string;
  admin?: boolean;
  group: string;
  advanced?: boolean;
  favoriteRecipes?: string[];
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  id: string;
  groupId: string;
  tokens?: LongLiveTokenOut[];
  cacheKey: string;
}
export interface LongLiveTokenOut {
  name: string;
  id: number;
  createdAt: string;
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
export interface LoingLiveTokenIn {
  name: string;
}
export interface LongLiveTokenInDB {
  name: string;
  userId: string;
  token: string;
  id: number;
  user: PrivateUser;
}
export interface PrivateUser {
  username?: string;
  fullName?: string;
  email: string;
  admin?: boolean;
  group: string;
  advanced?: boolean;
  favoriteRecipes?: string[];
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  id: string;
  groupId: string;
  tokens?: LongLiveTokenOut[];
  cacheKey: string;
  password: string;
}
export interface PrivatePasswordResetToken {
  userId: string;
  token: string;
  user: PrivateUser;
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
  id?: number;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: number;
  name: string;
  slug: string;
}
export interface RecipeTool {
  id?: number;
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
  referenceId?: string;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: number;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
}
export interface IngredientFood {
  name: string;
  description?: string;
  labelId?: string;
  id: number;
  label?: MultiPurposeLabelSummary;
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
  labelId?: string;
}
export interface ResetPassword {
  token: string;
  email: string;
  password: string;
  passwordConfirm: string;
}
export interface SavePasswordResetToken {
  userId: string;
  token: string;
}
export interface SignUpIn {
  name: string;
  admin: boolean;
}
export interface SignUpOut {
  name: string;
  admin: boolean;
  token: string;
  id: number;
}
export interface SignUpToken {
  name: string;
  admin: boolean;
  token: string;
}
export interface Token {
  access_token: string;
  token_type: string;
}
export interface TokenData {
  username?: string;
}
export interface UpdateGroup {
  name: string;
  id: string;
  categories?: CategoryBase[];
  webhooks?: unknown[];
}
export interface UserBase {
  username?: string;
  fullName?: string;
  email: string;
  admin?: boolean;
  group?: string;
  advanced?: boolean;
  favoriteRecipes?: string[];
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
}
export interface UserFavorites {
  username?: string;
  fullName?: string;
  email: string;
  admin?: boolean;
  group?: string;
  advanced?: boolean;
  favoriteRecipes?: RecipeSummary[];
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
}
export interface UserIn {
  username?: string;
  fullName?: string;
  email: string;
  admin?: boolean;
  group?: string;
  advanced?: boolean;
  favoriteRecipes?: string[];
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  password: string;
}
export interface ValidateResetToken {
  token: string;
}
