/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type PlanEntryType = "breakfast" | "lunch" | "dinner" | "side";
export type PlanRulesDay = "monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday" | "unset";
export type PlanRulesType = "breakfast" | "lunch" | "dinner" | "side" | "unset";

export interface Category {
  id: string;
  name: string;
  slug: string;
}
export interface CreatePlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  quantity?: number;
  text?: string;
  recipeId?: string;
}
export interface CreateRandomEntry {
  date: string;
  entryType?: PlanEntryType & string;
}
export interface ListItem {
  title?: string;
  text?: string;
  quantity?: number;
  checked?: boolean;
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
export interface MealDayOut {
  date?: string;
  meals: MealIn[];
  id: number;
}
export interface MealPlanIn {
  group: string;
  startDate: string;
  endDate: string;
  planDays: MealDayIn[];
}
export interface MealPlanOut {
  group: string;
  startDate: string;
  endDate: string;
  planDays: MealDayIn[];
  id: number;
  shoppingList?: number;
}
export interface PlanRulesCreate {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: Category[];
  tags?: Tag[];
}
export interface Tag {
  id: string;
  name: string;
  slug: string;
}
export interface PlanRulesOut {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: Category[];
  tags?: Tag[];
  groupId: string;
  id: string;
}
export interface PlanRulesSave {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: Category[];
  tags?: Tag[];
  groupId: string;
}
export interface ReadPlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string;
  id: number;
  quantity: number;
  groupId: string;
  userId?: string;
  recipe?: RecipeSummary;
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
export interface SavePlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string;
  groupId: string;
  userId?: string;
}
export interface ShoppingListIn {
  name: string;
  group?: string;
  items: ListItem[];
}
export interface ShoppingListOut {
  name: string;
  group?: string;
  items: ListItem[];
  id: number;
}
export interface UpdatePlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string;
  id: number;
  groupId: string;
  userId?: string;
}
