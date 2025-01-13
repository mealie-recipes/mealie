/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type LogicalOperator = "AND" | "OR";
export type RelationalKeyword = "IS" | "IS NOT" | "IN" | "NOT IN" | "CONTAINS ALL" | "LIKE" | "NOT LIKE";
export type RelationalOperator = "=" | "<>" | ">" | "<" | ">=" | "<=";

export interface CreateCookBook {
  name: string;
  description?: string;
  slug?: string | null;
  position?: number;
  public?: boolean;
  queryFilterString?: string;
}
export interface ReadCookBook {
  name: string;
  description?: string;
  slug?: string | null;
  position?: number;
  public?: boolean;
  queryFilterString?: string;
  groupId: string;
  householdId: string;
  id: string;
  queryFilter?: QueryFilterJSON;
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
export interface RecipeCookBook {
  name: string;
  description?: string;
  slug?: string | null;
  position?: number;
  public?: boolean;
  queryFilterString?: string;
  groupId: string;
  householdId: string;
  id: string;
  queryFilter?: QueryFilterJSON;
  recipes: RecipeSummary[];
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
export interface SaveCookBook {
  name: string;
  description?: string;
  slug?: string | null;
  position?: number;
  public?: boolean;
  queryFilterString?: string;
  groupId: string;
  householdId: string;
}
export interface UpdateCookBook {
  name: string;
  description?: string;
  slug?: string | null;
  position?: number;
  public?: boolean;
  queryFilterString?: string;
  groupId: string;
  householdId: string;
  id: string;
}
