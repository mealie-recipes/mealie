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
  text?: string;
  recipeId?: string | null;
}
export interface CreateRandomEntry {
  date: string;
  entryType?: PlanEntryType & string;
}
export interface ListItem {
  title?: string | null;
  text?: string;
  quantity?: number;
  checked?: boolean;
}
export interface PlanCategory {
  id: string;
  name: string;
  slug: string;
}
export interface PlanHousehold {
  id: string;
  name: string;
  slug: string;
}
export interface PlanRulesCreate {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: PlanCategory[];
  tags?: PlanTag[];
  households?: PlanHousehold[];
}
export interface PlanTag {
  id: string;
  name: string;
  slug: string;
}
export interface PlanRulesOut {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: PlanCategory[];
  tags?: PlanTag[];
  households?: PlanHousehold[];
  groupId: string;
  householdId: string;
  id: string;
}
export interface PlanRulesSave {
  day?: PlanRulesDay & string;
  entryType?: PlanRulesType & string;
  categories?: PlanCategory[];
  tags?: PlanTag[];
  households?: PlanHousehold[];
  groupId: string;
  householdId: string;
}
export interface ReadPlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string | null;
  id: number;
  groupId: string;
  userId?: string | null;
  householdId: string;
  recipe?: RecipeSummary | null;
}
export interface RecipeSummary {
  id?: string | null;
  userId?: string;
  householdId?: string;
  groupId?: string;
  name?: string | null;
  slug?: string;
  image?: unknown;
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
  onHand?: boolean;
}
export interface SavePlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string | null;
  groupId: string;
  userId?: string | null;
}
export interface ShoppingListIn {
  name: string;
  group?: string | null;
  items: ListItem[];
}
export interface ShoppingListOut {
  name: string;
  group?: string | null;
  items: ListItem[];
  id: number;
}
export interface UpdatePlanEntry {
  date: string;
  entryType?: PlanEntryType & string;
  title?: string;
  text?: string;
  recipeId?: string | null;
  id: number;
  groupId: string;
  userId?: string | null;
}
