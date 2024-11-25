/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface OpenAIIngredient {
  input: string;
  confidence?: number | null;
  quantity?: number | null;
  unit?: string | null;
  food?: string | null;
  note?: string | null;
}
export interface OpenAIIngredients {
  ingredients?: OpenAIIngredient[];
}
export interface OpenAIRecipe {
  name: string;
  description: string | null;
  recipe_yield?: string | null;
  total_time?: string | null;
  prep_time?: string | null;
  perform_time?: string | null;
  ingredients?: OpenAIRecipeIngredient[];
  instructions?: OpenAIRecipeInstruction[];
  notes?: OpenAIRecipeNotes[];
}
export interface OpenAIRecipeIngredient {
  title?: string | null;
  text: string;
}
export interface OpenAIRecipeInstruction {
  title?: string | null;
  text: string;
}
export interface OpenAIRecipeNotes {
  title?: string | null;
  text: string;
}
export interface OpenAIBase {}
