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
  parentId: number;
  token: string;
}
export interface GroupBase {
  name: string;
}
export interface GroupInDB {
  name: string;
  id: number;
  categories?: CategoryBase[];
  webhookUrls?: string[];
  webhookTime?: string;
  webhookEnable: boolean;
  users?: UserOut[];
  mealplans?: MealPlanOut[];
  shoppingLists?: ShoppingListOut[];
}
export interface UserOut {
  username?: string;
  fullName?: string;
  email: string;
  admin: boolean;
  group: string;
  favoriteRecipes?: string[];
  id: number;
  tokens?: LongLiveTokenOut[];
}
export interface LongLiveTokenOut {
  name: string;
  id: number;
}
export interface MealPlanOut {
  group: string;
  startDate: string;
  endDate: string;
  planDays: MealDayIn[];
  uid: number;
  shoppingList?: number;
}
export interface MealDayIn {
  date?: string;
  meals: MealIn[];
}
export interface MealIn {
  slug?: string;
  name?: string;
  description?: string;
}
export interface ShoppingListOut {
  name: string;
  group?: string;
  items: ListItem[];
  id: number;
}
export interface ListItem {
  title?: string;
  text?: string;
  quantity?: number;
  checked?: boolean;
}
export interface LoingLiveTokenIn {
  name: string;
}
export interface LongLiveTokenInDB {
  name: string;
  parentId: number;
  token: string;
  id: number;
  user: UserInDB;
}
export interface UserInDB {
  username?: string;
  fullName?: string;
  email: string;
  admin: boolean;
  group: string;
  favoriteRecipes?: string[];
  id: number;
  tokens?: LongLiveTokenOut[];
  password: string;
}
export interface RecipeSummary {
  id?: number;
  name?: string;
  slug?: string;
  image?: unknown;
  description?: string;
  recipeCategory?: string[];
  tags?: string[];
  rating?: number;
  dateAdded?: string;
  dateUpdated?: string;
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
  id: number;
  categories?: CategoryBase[];
  webhookUrls?: string[];
  webhookTime?: string;
  webhookEnable: boolean;
}
export interface UserBase {
  username?: string;
  fullName?: string;
  email: string;
  admin: boolean;
  group?: string;
  favoriteRecipes?: string[];
}
export interface UserFavorites {
  username?: string;
  fullName?: string;
  email: string;
  admin: boolean;
  group?: string;
  favoriteRecipes?: RecipeSummary[];
}
export interface UserIn {
  username?: string;
  fullName?: string;
  email: string;
  admin: boolean;
  group?: string;
  favoriteRecipes?: string[];
  password: string;
}
