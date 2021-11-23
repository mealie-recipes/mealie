import { Category } from "../categories";
import { Tag } from "../tags";

export type Parser = "nlp" | "brute";

export interface Confidence {
  average?: number;
  comment?: number;
  name?: number;
  unit?: number;
  quantity?: number;
  food?: number;
}

export interface Unit {
  name: string;
  description: string;
  fraction: boolean;
  abbreviation: string;
}

export interface Food {
  name: string;
  description?: string;
}

export interface Ingredient {
  referenceId: string;
  title: string;
  note: string;
  unit: Unit | null;
  food: Food | null;
  disableAmount: boolean;
  quantity: number;
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
  file?: File;
}

export interface RecipeCommentCreate {
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
  recipe_id: number;
  user_id: number;
  user: RecipeCommentUser;
}
