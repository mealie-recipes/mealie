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
