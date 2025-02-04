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
  group?: string | null;
  household?: string | null;
  groupToken?: string | null;
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
export interface GroupHouseholdSummary {
  id: string;
  name: string;
}
export interface GroupInDB {
  name: string;
  id: string;
  slug: string;
  categories?: CategoryBase[] | null;
  webhooks?: ReadWebhook[];
  households?: GroupHouseholdSummary[] | null;
  users?: UserSummary[] | null;
  preferences?: ReadGroupPreferences | null;
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
  webhookType?: WebhookType;
  scheduledTime: string;
  groupId: string;
  householdId: string;
  id: string;
}
export interface UserSummary {
  id: string;
  groupId: string;
  householdId: string;
  username: string;
  fullName: string;
}
export interface ReadGroupPreferences {
  privateGroup?: boolean;
  groupId: string;
  id: string;
}
export interface GroupSummary {
  name: string;
  id: string;
  slug: string;
  preferences?: ReadGroupPreferences | null;
}
export interface LongLiveTokenCreateResponse {
  name: string;
  id: number;
  createdAt?: string | null;
  token: string;
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
  username?: string | null;
  fullName?: string | null;
  email: string;
  authMethod?: AuthMethod;
  admin?: boolean;
  group: string;
  household: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canManageHousehold?: boolean;
  canOrganize?: boolean;
  groupId: string;
  groupSlug: string;
  householdId: string;
  householdSlug: string;
  tokens?: LongLiveTokenOut[] | null;
  cacheKey: string;
  password: string;
  loginAttemps?: number;
  lockedAt?: string | null;
}
export interface LongLiveTokenOut {
  name: string;
  id: number;
  createdAt?: string | null;
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
  user_id?: string | null;
  username?: string | null;
}
export interface UnlockResults {
  unlocked?: number;
}
export interface UpdateGroup {
  name: string;
  id: string;
  slug: string;
  categories?: CategoryBase[] | null;
  webhooks?: CreateWebhook[];
}
export interface CreateWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  webhookType?: WebhookType;
  scheduledTime: string;
}
export interface UserBase {
  id?: string | null;
  username?: string | null;
  fullName?: string | null;
  email: string;
  authMethod?: AuthMethod;
  admin?: boolean;
  group?: string | null;
  household?: string | null;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canManageHousehold?: boolean;
  canOrganize?: boolean;
}
export interface UserIn {
  id?: string | null;
  username: string;
  fullName: string;
  email: string;
  authMethod?: AuthMethod;
  admin?: boolean;
  group?: string | null;
  household?: string | null;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canManageHousehold?: boolean;
  canOrganize?: boolean;
  password: string;
}
export interface UserOut {
  id: string;
  username?: string | null;
  fullName?: string | null;
  email: string;
  authMethod?: AuthMethod;
  admin?: boolean;
  group: string;
  household: string;
  advanced?: boolean;
  canInvite?: boolean;
  canManage?: boolean;
  canManageHousehold?: boolean;
  canOrganize?: boolean;
  groupId: string;
  groupSlug: string;
  householdId: string;
  householdSlug: string;
  tokens?: LongLiveTokenOut[] | null;
  cacheKey: string;
}
export interface UserRatingCreate {
  recipeId: string;
  rating?: number | null;
  isFavorite?: boolean;
  userId: string;
}
export interface UserRatingOut {
  recipeId: string;
  rating?: number | null;
  isFavorite?: boolean;
  userId: string;
  id: string;
}
export interface UserRatingSummary {
  recipeId: string;
  rating?: number | null;
  isFavorite?: boolean;
}
export interface UserRatingUpdate {
  rating?: number | null;
  isFavorite?: boolean | null;
}
export interface ValidateResetToken {
  token: string;
}
