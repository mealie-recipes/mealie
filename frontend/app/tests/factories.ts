import type { Recipe, RecipeSummary } from "~/lib/api/types/recipe";

export function makeRecipeSummary(overrides: Partial<RecipeSummary> = {}): RecipeSummary {
  return {
    id: "recipe-id",
    userId: "user-id",
    householdId: "household-id",
    groupId: "group-id",
    name: "Recipe",
    slug: "recipe",
    image: null,
    recipeServings: 0,
    recipeYieldQuantity: 0,
    recipeYield: null,
    totalTime: null,
    prepTime: null,
    performTime: null,
    totalTimeSeconds: null,
    prepTimeSeconds: null,
    performTimeSeconds: null,
    description: "",
    recipeCategory: [],
    tags: [],
    tools: [],
    rating: null,
    orgURL: null,
    dateAdded: null,
    dateUpdated: null,
    createdAt: null,
    updatedAt: null,
    ...overrides,
  };
}

export function makeRecipe(overrides: Partial<Recipe> = {}): Recipe {
  return {
    ...makeRecipeSummary(),
    recipeIngredient: [],
    recipeInstructions: [],
    nutrition: null,
    settings: null,
    assets: [],
    notes: [],
    extras: {},
    comments: [],
    ...overrides,
  };
}
