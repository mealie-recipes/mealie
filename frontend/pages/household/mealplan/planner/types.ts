import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import type { Nutrition } from "~/lib/api/types/recipe";

export type MealsByDate = {
  date: Date;
  meals: ReadPlanEntry[];
};

export type NutritionByDate = {
  show: boolean;
  date: Date;
  nutrition: Nutrition;
};
