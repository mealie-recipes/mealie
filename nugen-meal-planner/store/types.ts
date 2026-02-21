export type IngredientCategory =
    | 'Proteins'
    | 'Veggies'
    | 'Carbs'
    | 'Fats'
    | 'Fermented'
    | 'Spices';

export interface Ingredient {
    id: string;
    name: string;
    category: IngredientCategory;
    isSelected?: boolean;
}

export interface UserPreferences {
    cookTimeMinutes: number;
    batchCookMode: boolean;
}

export interface RecipeIngredient {
    ingredientId: string;
    name: string;
    quantity: number;
    unit: string;
}

export interface Recipe {
    id: string;
    title: string;
    description: string;
    prepTimeMinutes: number;
    ingredients: RecipeIngredient[];
    instructions: string[];
    imageUrl?: string;
    tags: string[];
}

export interface WeeklyPlan {
    [day: string]: Recipe[]; // 'Monday' -> [Recipe1, Recipe2]
}
