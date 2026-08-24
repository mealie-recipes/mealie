/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface OpenAICompiledSource {
  contains_recipe: boolean;
  content: string;
  language?: string | null;
  image_url?: string | null;
}
export interface OpenAIIngredient {
  quantity?: number | null;
  unit?: string | null;
  food?: string | null;
  note?: string | null;
}
export interface OpenAIIngredients {
  ingredients?: OpenAIIngredient[];
}
export interface OpenAIOrganizers {
  tags?: string[];
  categories?: string[];
  tools?: string[];
}
export interface OpenAIRecipe {
  name: string;
  description?: string | null;
  recipe_yield?: string | null;
  total_time?: string | null;
  prep_time?: string | null;
  perform_time?: string | null;
  ingredients?: OpenAIRecipeIngredient[];
  instructions?: OpenAIRecipeInstruction[];
  notes?: OpenAIRecipeNotes[];
  nutrition?: OpenAIRecipeNutrition | null;
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
export interface OpenAIRecipeNutrition {
  calories?: string | null;
  carbohydrate_content?: string | null;
  cholesterol_content?: string | null;
  fat_content?: string | null;
  fiber_content?: string | null;
  protein_content?: string | null;
  saturated_fat_content?: string | null;
  sodium_content?: string | null;
  sugar_content?: string | null;
  trans_fat_content?: string | null;
  unsaturated_fat_content?: string | null;
}
export interface OpenAIText {
  text: string;
}
export interface OpenAIBase {}
