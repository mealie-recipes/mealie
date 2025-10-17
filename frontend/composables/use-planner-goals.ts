/**
 * Composable for managing meal planner goals (calories and macros)
 *
 * Goals are persisted to localStorage and provide daily targets
 * for tracking nutritional intake in the meal planner.
 */

import { computed, ref } from "vue";

const STORAGE_KEY = "planner.goals.v1";

export interface PlannerGoals {
  calories: number;
  protein: number;
  carbohydrate: number;
  fat: number;
  toleranceKcal?: number; // Optional: how many kcal +/- is still "ok"
}

const DEFAULT_GOALS: PlannerGoals = {
  calories: 2400,
  protein: 160,
  carbohydrate: 250,
  fat: 80,
  toleranceKcal: 0,
};

/**
 * Load goals from localStorage
 */
function loadGoals(): PlannerGoals {
  if (typeof window === "undefined") {
    return { ...DEFAULT_GOALS };
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Merge with defaults to handle missing fields
      return {
        ...DEFAULT_GOALS,
        ...parsed,
      };
    }
  } catch (error) {
    console.warn("Failed to load planner goals from localStorage:", error);
  }

  return { ...DEFAULT_GOALS };
}

/**
 * Save goals to localStorage
 */
function saveGoals(goals: PlannerGoals): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(goals));
  } catch (error) {
    console.warn("Failed to save planner goals to localStorage:", error);
  }
}

// Shared reactive state
const goalsState = ref<PlannerGoals>(loadGoals());

/**
 * Composable for accessing and managing planner goals
 */
export function usePlannerGoals() {
  const goals = computed({
    get: () => goalsState.value,
    set: (value: PlannerGoals) => {
      goalsState.value = value;
      saveGoals(value);
    },
  });

  function setGoals(newGoals: Partial<PlannerGoals>): void {
    goals.value = {
      ...goals.value,
      ...newGoals,
    };
  }

  function resetGoals(): void {
    goals.value = { ...DEFAULT_GOALS };
  }

  return {
    goals,
    setGoals,
    resetGoals,
  };
}
