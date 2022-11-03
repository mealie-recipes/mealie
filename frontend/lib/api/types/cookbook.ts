/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CreateCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  public?: boolean;
  categories?: CategoryBase[];
  tags?: TagBase[];
  tools?: RecipeTool[];
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
}
export interface CategoryBase {
  name: string;
  id: string;
  slug: string;
}
export interface TagBase {
  name: string;
  id: string;
  slug: string;
}
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  onHand?: boolean;
}
export interface ReadCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  public?: boolean;
  categories?: CategoryBase[];
  tags?: TagBase[];
  tools?: RecipeTool[];
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  groupId: string;
  id: string;
}
export interface RecipeCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  public?: boolean;
  categories?: CategoryBase[];
  tags?: TagBase[];
  tools?: RecipeTool[];
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  groupId: string;
  id: string;
  recipes: RecipeSummary[];
}
export interface RecipeSummary {
  id?: string;
  userId?: string;
  groupId?: string;
  name?: string;
  slug?: string;
  image?: unknown;
  recipeYield?: string;
  totalTime?: string;
  prepTime?: string;
  cookTime?: string;
  performTime?: string;
  description?: string;
  recipeCategory?: RecipeCategory[];
  tags?: RecipeTag[];
  tools?: RecipeTool[];
  rating?: number;
  orgURL?: string;
  recipeIngredient?: RecipeIngredient[];
  dateAdded?: string;
  dateUpdated?: string;
  createdAt?: string;
  updateAt?: string;
  lastMade?: string;
}
export interface RecipeCategory {
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeIngredient {
  title?: string;
  note?: string;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  disableAmount?: boolean;
  quantity?: number;
  originalText?: string;
  referenceId?: string;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  useAbbreviation?: boolean;
  id: string;
  createdAt?: string;
  updateAt?: string;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  fraction?: boolean;
  abbreviation?: string;
  useAbbreviation?: boolean;
}
export interface IngredientFood {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
  id: string;
  label?: MultiPurposeLabelSummary;
  createdAt?: string;
  updateAt?: string;
}
export interface MultiPurposeLabelSummary {
  name: string;
  color?: string;
  groupId: string;
  id: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
  extras?: {
    [k: string]: unknown;
  };
  labelId?: string;
}
export interface SaveCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  public?: boolean;
  categories?: CategoryBase[];
  tags?: TagBase[];
  tools?: RecipeTool[];
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  groupId: string;
}
export interface UpdateCookBook {
  name: string;
  description?: string;
  slug?: string;
  position?: number;
  public?: boolean;
  categories?: CategoryBase[];
  tags?: TagBase[];
  tools?: RecipeTool[];
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  groupId: string;
  id: string;
}
