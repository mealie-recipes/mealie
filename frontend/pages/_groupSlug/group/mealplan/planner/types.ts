import { ReadPlanEntry } from "~/lib/api/types/meal-plan";

export type MealsByDate = {
  date: Date;
  meals: ReadPlanEntry[]
}
