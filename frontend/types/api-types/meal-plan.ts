/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

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
  uid: number;
  shoppingList?: number;
}
export interface ShoppingList {
  name: string;
  group?: string;
  items: ListItem[];
  id: number;
}
