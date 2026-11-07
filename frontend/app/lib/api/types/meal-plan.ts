/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type PlanEntryType = "breakfast" | "lunch" | "dinner" | "side" | "snack" | "drink" | "dessert";
export type PlanRulesDay = "monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday" | "unset";
export type PlanRulesType = "breakfast" | "lunch" | "dinner" | "side" | "snack" | "drink" | "dessert" | "unset";
export type LogicalOperator = "AND" | "OR";
export type RelationalKeyword = "IS" | "IS NOT" | "IN" | "NOT IN" | "CONTAINS ALL" | "LIKE" | "NOT LIKE";
export type RelationalOperator = "=" | "<>" | ">" | "<" | ">=" | "<=";

export interface MealPlanICalTokenOut {
  householdId: string;
  mealplanIcalToken: string | null;
}
export interface PlanEntryCreate {
  date: string;
  endDate?: string | null;
  entryType?: PlanEntryType;
  title?: string;
  text?: string;
  recipeId?: string | null;
  recipeScale?: number;
}
export interface PlanEntryOut {
  date: string;
  endDate: string | null;
  entryType: PlanEntryType;
  title: string;
  text: string;
  recipeId: string | null;
  recipeScale: number;
  id: number;
  groupId: string;
  userId: string;
  householdId: string;
  recipe: RecipeSummary | null;
  updatedAt: string | null;
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
export interface PlanEntrySave {
  date: string;
  endDate?: string | null;
  entryType?: PlanEntryType;
  title?: string;
  text?: string;
  recipeId?: string | null;
  recipeScale?: number;
  groupId: string;
  userId: string;
}
export interface PlanEntryUpdate {
  date: string;
  endDate?: string | null;
  entryType?: PlanEntryType;
  title?: string;
  text?: string;
  recipeId?: string | null;
  recipeScale?: number;
  id: number;
  groupId: string;
  userId: string;
}
export interface PlanRulesCreate {
  day?: PlanRulesDay;
  entryType?: PlanRulesType;
  queryFilterString?: string;
}
export interface PlanRulesOut {
  day: PlanRulesDay;
  entryType: PlanRulesType;
  queryFilterString: string;
  groupId: string;
  householdId: string;
  id: string;
  queryFilter: QueryFilterJSON;
}
export interface QueryFilterJSON {
  parts?: QueryFilterJSONPart[];
}
export interface QueryFilterJSONPart {
  leftParenthesis?: string | null;
  rightParenthesis?: string | null;
  logicalOperator?: LogicalOperator | null;
  attributeName?: string | null;
  relationalOperator?: RelationalKeyword | RelationalOperator | null;
  value?: string | string[] | null;
  [k: string]: unknown;
}
export interface PlanRulesSave {
  day?: PlanRulesDay;
  entryType?: PlanRulesType;
  queryFilterString?: string;
  groupId: string;
  householdId: string;
}
export interface RandomPlanEntryCreate {
  date: string;
  endDate?: string | null;
  entryType?: PlanEntryType;
}
export interface MealieOutModel {}
