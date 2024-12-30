/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type OrderByNullPosition = "first" | "last";
export type OrderDirection = "asc" | "desc";
export type LogicalOperator = "AND" | "OR";
export type RelationalKeyword = "IS" | "IS NOT" | "IN" | "NOT IN" | "CONTAINS ALL" | "LIKE" | "NOT LIKE";
export type RelationalOperator = "=" | "<>" | ">" | "<" | ">=" | "<=";

export interface ErrorResponse {
  message: string;
  error?: boolean;
  exception?: string | null;
}
export interface FileTokenResponse {
  fileToken: string;
}
export interface PaginationQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
  page?: number;
  perPage?: number;
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
}
export interface RecipeSearchQuery {
  cookbook?: string | null;
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  requireAllFoods?: boolean;
  search?: string | null;
}
export interface RequestQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
}
export interface SuccessResponse {
  message: string;
  error?: boolean;
}
export interface ValidationResponse {
  valid: boolean;
}
