/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface IngredientFood {
  name: string;
  description?: string;
  id: number;
}
export interface MultiPurposeLabelCreate {
  name: string;
}
export interface MultiPurposeLabelOut {
  name: string;
  groupId: string;
  id: string;
  shoppingListItems?: ShoppingListItemOut[];
  foods?: IngredientFood[];
}
export interface ShoppingListItemOut {
  shoppingListId: string;
  checked?: boolean;
  position?: number;
  isFood?: boolean;
  note?: string;
  quantity?: number;
  unitId?: number;
  unit?: IngredientUnit;
  foodId?: number;
  food?: IngredientFood;
  recipeId?: number;
  labelId?: string;
  id: string;
  label?: MultiPurposeLabelSummary;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: number;
}
export interface MultiPurposeLabelSummary {
  name: string;
  groupId: string;
  id: string;
}
export interface MultiPurposeLabelSave {
  name: string;
  groupId: string;
}
export interface MultiPurposeLabelUpdate {
  name: string;
  groupId: string;
  id: string;
}
