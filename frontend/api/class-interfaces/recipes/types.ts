import { Category } from "../categories";
import { Tag } from "../tags";
import { CreateIngredientFood, CreateIngredientUnit, IngredientFood, IngredientUnit } from "~/types/api-types/recipe";

export type Parser = "nlp" | "brute";

export interface Confidence {
  average?: number;
  comment?: number;
  name?: number;
  unit?: number;
  quantity?: number;
  food?: number;
}

export interface Ingredient {
  title?: string;
  note?: string;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  disableAmount?: boolean;
  quantity?: number;
  referenceId?: string;
}

export interface ParsedIngredient {
  confidence: Confidence;
  ingredient: Ingredient;
}

export interface BulkCreateRecipe {
  url: string;
  categories: Category[];
  tags: Tag[];
}

export interface BulkCreatePayload {
  imports: BulkCreateRecipe[];
}

export interface RecipeZipToken {
  token: string;
}

export interface CreateAsset {
  name: string;
  icon: string;
  extension: string;
  file: File;
}

export interface RecipeCommentCreate {
  recipeId: string;
  text: string;
}

export interface RecipeCommentUpdate extends RecipeCommentCreate {
  id: string;
}

interface RecipeCommentUser {
  id: string;
  username: string;
  admin: boolean;
}

export interface RecipeComment extends RecipeCommentUpdate {
  createdAt: any;
  updatedAt: any;
  userId: number;
  user: RecipeCommentUser;
}
