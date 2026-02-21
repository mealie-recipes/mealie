import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ingredient, Recipe, UserPreferences, WeeklyPlan } from './types';

interface FoodState {
    hasCompletedSetup: boolean;
    userIngredients: Ingredient[];
    userPreferences: UserPreferences;
    generatedRecipes: Recipe[];
    weeklyPlan: WeeklyPlan;
    isAiOptimizationMode: boolean;

    // Actions
    completeSetup: () => void;
    setUserIngredients: (ingredients: Ingredient[]) => void;
    setUserPreferences: (preferences: UserPreferences) => void;
    setGeneratedRecipes: (recipes: Recipe[]) => void;
    addToWeeklyPlan: (day: string, recipe: Recipe) => void;
    removeFromWeeklyPlan: (day: string, recipeId: string) => void;
    toggleAiOptimizationMode: () => void;
    clearPlan: () => void;
}

export const useFoodStore = create<FoodState>()(
    persist(
        (set) => ({
            hasCompletedSetup: false,
            userIngredients: [],
            userPreferences: {
                cookTimeMinutes: 30,
                batchCookMode: false,
            },
            generatedRecipes: [],
            weeklyPlan: {
                Monday: [],
                Tuesday: [],
                Wednesday: [],
                Thursday: [],
                Friday: [],
                Saturday: [],
                Sunday: [],
            },
            isAiOptimizationMode: false,

            completeSetup: () => set({ hasCompletedSetup: true }),
            setUserIngredients: (ingredients) => set({ userIngredients: ingredients }),
            setUserPreferences: (preferences) => set({ userPreferences: preferences }),
            setGeneratedRecipes: (recipes) => set({ generatedRecipes: recipes }),
            addToWeeklyPlan: (day, recipe) =>
                set((state) => ({
                    weeklyPlan: {
                        ...state.weeklyPlan,
                        [day]: [...state.weeklyPlan[day], recipe],
                    },
                })),
            removeFromWeeklyPlan: (day, recipeId) =>
                set((state) => ({
                    weeklyPlan: {
                        ...state.weeklyPlan,
                        [day]: state.weeklyPlan[day].filter((r) => r.id !== recipeId),
                    },
                })),
            toggleAiOptimizationMode: () =>
                set((state) => ({ isAiOptimizationMode: !state.isAiOptimizationMode })),
            clearPlan: () =>
                set({
                    weeklyPlan: {
                        Monday: [],
                        Tuesday: [],
                        Wednesday: [],
                        Thursday: [],
                        Friday: [],
                        Saturday: [],
                        Sunday: [],
                    },
                }),
        }),
        {
            name: 'nugen-food-storage',
            storage: createJSONStorage(() => AsyncStorage),
        }
    )
);
