/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type WebhookType = "mealplan";
export type AuthMethod = "Mealie" | "LDAP" | "OIDC";

export interface ChangePassword {
  currentPassword?: string;
  newPassword: string;
}
export interface CreateToken {
  name: string;
  integrationId?: string;
  userId: string;
  token: string;
}
export interface CreateUserRegistration {
  group?: string;
  groupToken?: string;
  email: string;
  username: string;
  fullName: string;
  password: string;
  passwordConfirm: string;
  advanced?: boolean;
  private?: boolean;
  seedData?: boolean;
  locale?: string;
}
export interface CredentialsRequest {
  username: string;
  password: string;
  remember_me?: boolean;
}
export interface DeleteTokenResponse {
  tokenDelete: string;
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
  slug: string;
  categories?: CategoryBase[];
  webhooks?: ReadWebhook[];
  users?: UserOut[];
  preferences?: ReadGroupPreferences;
}
export interface GroupSummary {
  name: string;
  id: string;
  slug: string;
  preferences?: ReadGroupPreferences;

}
export interface CategoryBase {
  name: string;
  id: string;
  slug: string;
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
export interface UserOut {
  id: string;
  username?: string;
  fullName?: string;
  email: string;
  authMethod?: AuthMethod & string;
  admin?: boolean;
  group: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  groupId: string;
  groupSlug: string;
  tokens?: LongLiveTokenOut[];
  cacheKey: string;
}
export interface LongLiveTokenOut {
  token: string;
  name: string;
  id: number;
  createdAt?: string;
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
export interface LongLiveTokenIn {
  name: string;
  integrationId?: string;
}
export interface LongLiveTokenInDB {
  name: string;
  integrationId?: string;
  userId: string;
  token: string;
  id: number;
  user: PrivateUser;
}
export interface PrivateUser {
  id: string;
  username?: string;
  fullName?: string;
  email: string;
  authMethod?: AuthMethod & string;
  admin?: boolean;
  group: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  groupId: string;
  groupSlug: string;
  tokens?: LongLiveTokenOut[];
  cacheKey: string;
  password: string;
  loginAttemps?: number;
  lockedAt?: string;
}
export interface OIDCRequest {
  id_token: string;
}
export interface PasswordResetToken {
  token: string;
}
export interface PrivatePasswordResetToken {
  userId: string;
  token: string;
  user: PrivateUser;
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
export interface Token {
  access_token: string;
  token_type: string;
}
export interface TokenData {
  user_id?: string;
  username?: string;
}
export interface UnlockResults {
  unlocked?: number;
}
export interface UpdateGroup {
  name: string;
  id: string;
  slug: string;
  categories?: CategoryBase[];
  webhooks?: CreateWebhook[];
}
export interface CreateWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType & string;
  scheduledTime: string;
}
export interface UserBase {
  id?: string;
  username?: string;
  fullName?: string;
  email: string;
  authMethod?: AuthMethod & string;
  admin?: boolean;
  group?: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
}
export interface UserIn {
  id?: string;
  username?: string;
  fullName?: string;
  email: string;
  authMethod?: AuthMethod & string;
  admin?: boolean;
  group?: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canOrganize?: boolean;
  password: string;
}
export interface UserRatingCreate {
  recipeId: string;
  rating?: number;
  isFavorite?: boolean;
  userId: string;
}
export interface UserRatingOut {
  recipeId: string;
  rating?: number;
  isFavorite?: boolean;
  userId: string;
  id: string;
}
export interface UserRatingSummary {
  recipeId: string;
  rating?: number;
  isFavorite?: boolean;
}
export interface UserSummary {
  id: string;
  fullName: string;
}
export interface ValidateResetToken {
  token: string;
}
