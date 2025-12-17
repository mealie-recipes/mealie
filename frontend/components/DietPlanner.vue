<template>
  <v-container class="mx-auto my-4" style="max-width: 960px;">
    <v-card class="pa-4 mb-4">
      <v-row align="center" justify="space-between">
        <v-col>
          <h1 class="text-h5">
            Diet Planner
          </h1>
          <p class="text-subtitle-1">
            Plan your weekly meals and track estimated calories.
          </p>
        </v-col>
      </v-row>
    </v-card>

    <!-- Calorie Goal -->
    <v-card class="pa-4 mb-4">
      <h2 class="text-subtitle-2 mb-2">
        Calorie Goal & Personal Info
      </h2>

      <!-- User Metrics Section -->
      <div class="mb-4">
        <h3 class="text-caption font-weight-bold mb-3 d-block">
          Personal Information
        </h3>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model.number="weight"
              label="Weight (kg)"
              type="number"
              dense
              outlined
              min="20"
              max="300"
              step="0.5"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model.number="height"
              label="Height (cm)"
              type="number"
              dense
              outlined
              min="100"
              max="250"
              step="1"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model.number="age"
              label="Age (years)"
              type="number"
              dense
              outlined
              min="10"
              max="120"
              step="1"
            />
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="gender"
              :items="['male', 'female']"
              label="Gender"
              dense
              outlined
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" sm="6">
            <v-select
              v-model="activityLevel"
              :items="activityLevelOptions"
              item-title="label"
              item-value="value"
              label="Activity Level"
              dense
              outlined
            />
          </v-col>
        </v-row>
      </div>

      <v-divider class="my-3" />

      <!-- Goal Selection Section -->
      <div>
        <h3 class="text-caption font-weight-bold mb-3 d-block">
          Calorie Adjustment Goal
        </h3>
        <v-row>
          <v-col cols="12" sm="6">
            <v-radio-group v-model="goal" row>
              <v-radio label="Lose" value="lose" />
              <v-radio label="Maintain" value="maintain" />
              <v-radio label="Gain" value="gain" />
            </v-radio-group>
          </v-col>
          <v-col cols="12" sm="6" class="d-flex align-center">
            <div>
              <div class="text-subtitle-1">
                Daily Target
              </div>
              <div class="text-h6">
                {{ dailyTarget }} kcal
              </div>
            </div>
          </v-col>
        </v-row>
      </div>
    </v-card>

    <!-- Weekly Plan -->
    <v-card class="pa-4 mb-4">
      <h2 class="text-subtitle-2 mb-2">
        Weekly Plan
      </h2>
      <div class="pa-2">
        <v-simple-table dense>
          <thead>
            <tr>
              <th class="text-left">
                Day
              </th>
              <th class="text-left">
                Breakfast
              </th>
              <th class="text-left">
                Lunch
              </th>
              <th class="text-left">
                Dinner
              </th>
              <th class="text-left">
                Total
              </th>
              <th class="text-left">
                vs Target
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="day in days" :key="day">
              <td class="text-left font-weight-medium">
                {{ capitalize(day) }}
              </td>
              <td>
                <v-select
                  v-model="weekPlan[day].breakfast"
                  :items="recipes"
                  item-title="name"
                  item-value="id"
                  dense
                  hide-details
                  clearable
                />
                <div class="text-caption mt-1">
                  Est: <strong>{{ _mealCalories[day].breakfast }} kcal</strong>
                </div>
              </td>
              <td>
                <v-select
                  v-model="weekPlan[day].lunch"
                  :items="recipes"
                  item-title="name"
                  item-value="id"
                  dense
                  hide-details
                  clearable
                />
                <div class="text-caption mt-1">
                  Est: <strong>{{ _mealCalories[day].lunch }} kcal</strong>
                </div>
              </td>
              <td>
                <v-select
                  v-model="weekPlan[day].dinner"
                  :items="recipes"
                  item-title="name"
                  item-value="id"
                  dense
                  hide-details
                  clearable
                />
                <div class="text-caption mt-1">
                  Est: <strong>{{ _mealCalories[day].dinner }} kcal</strong>
                </div>
              </td>
              <td>
                <div class="text-caption">
                  <strong>{{ getDayCalories(day) }} kcal</strong>
                </div>
              </td>
              <td>
                <div
                  class="text-caption font-weight-bold"
                  :class="getDayTargetClass(day)"
                >
                  {{ getDayTargetText(day) }}
                </div>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </div>
    </v-card>

    <!-- Summary -->
    <v-card class="pa-4 mb-4">
      <h2 class="text-subtitle-2 mb-2">
        Summary &amp; Health Suggestions
      </h2>
      <div class="pa-2" style="min-height: 200px; background: transparent;">
        <!-- Summary: calorie goal and totals -->
        <div class="text-caption">
          Calorie goal: <strong>{{ goal || '—' }}</strong>
        </div>
        <div class="text-caption">
          Daily target: <strong>{{ dailyTarget }} kcal</strong>
        </div>
        <v-divider class="my-3" />

        <!-- Weekly Overview Stats -->
        <div class="text-subtitle-2 mb-2">
          Weekly Overview
        </div>
        <div class="pa-2 mb-3" style="background-color: rgba(0,0,0,0.04); border-radius: 4px;">
          <div class="text-caption mb-1">
            Weekly Total: <strong class="text-h6">{{ _weeklyTotal }} kcal</strong>
          </div>
          <div class="text-caption mb-1">
            Average Per Day: <strong>{{ averagePerDay }} kcal</strong>
          </div>
          <div class="text-caption mb-1">
            Days Over Target:
            <strong class="error--text">{{ daysOverTarget }}</strong>
          </div>
          <div class="text-caption">
            Days Under Target:
            <strong class="success--text">{{ daysUnderTarget }}</strong>
          </div>
        </div>

        <v-divider class="my-3" />

        <!-- Daily Breakdown -->
        <div class="text-subtitle-2 mb-2">
          Daily Totals
        </div>
        <div>
          <div v-for="d in days" :key="d" class="text-caption mb-1">
            {{ capitalize(d) }}: <strong>{{ getDayCalories(d) }} kcal</strong>
            <span :class="getDayTargetClass(d)">— {{ getDayTargetText(d) }}</span>
          </div>
        </div>

        <v-divider class="my-3" />

        <!-- Health Suggestions -->
        <div class="text-subtitle-2 mb-2">
          Health Suggestions
        </div>
        <div v-if="healthSuggestions.length > 0" class="pa-2 mb-3" style="background-color: rgba(76,175,80,0.08); border-radius: 4px; border-left: 4px solid #4caf50;">
          <ul class="text-caption" style="margin: 0; padding-left: 20px;">
            <li v-for="(suggestion, idx) in healthSuggestions" :key="idx" class="mb-1">
              {{ suggestion }}
            </li>
          </ul>
        </div>
        <div v-else class="text-caption pa-2 mb-3" style="background-color: rgba(0,0,0,0.04); border-radius: 4px;">
          Keep tracking to receive personalized suggestions!
        </div>

        <div class="text-caption" style="color: rgba(0,0,0,0.6);">
          <em>Disclaimer: These are general suggestions only and not medical advice.</em>
        </div>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { allRecipes, useRecipes } from "~/composables/recipes";
import { useUserApi } from "~/composables/api";

type Goal = "lose" | "maintain" | "gain";
type MealEntry = string | null;
type MealDay = { breakfast: MealEntry; lunch: MealEntry; dinner: MealEntry };
type WeekPlan = Record<"monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday", MealDay>;

const STORAGE_WEEK_KEY = "dietPlannerWeekPlan";

const days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] as const;

// Recipes are provided by the existing composable `use-recipes`
const recipes = allRecipes;

// Cache for full recipe data with ingredients
const _fullRecipeCache = ref<Map<string, any>>(new Map());
const _api = useUserApi();

// Activity level options
const activityLevelOptions = [
  { label: "Low (sedentary)", value: "low" },
  { label: "Moderate (some exercise)", value: "moderate" },
  { label: "High (regular exercise)", value: "high" },
];

// User metrics state
const weight = ref<number | null>(null); // kg
const height = ref<number | null>(null); // cm
const age = ref<number | null>(null); // years
const gender = ref<"male" | "female" | null>(null);
const activityLevel = ref<"low" | "moderate" | "high">("moderate");

// Goal state
const goal = ref<Goal | null>(null);

// Calculate BMR using Mifflin-St Jeor equation
const bmr = computed(() => {
  if (!weight.value || !height.value || !age.value || !gender.value) return 0;

  const w = weight.value;
  const h = height.value;
  const a = age.value;

  if (gender.value === "male") {
    return (10 * w) + (6.25 * h) - (5 * a) + 5;
  }
  // female
  return (10 * w) + (6.25 * h) - (5 * a) - 161;
});

// Apply activity multiplier to get TDEE (Total Daily Energy Expenditure)
const tdee = computed(() => {
  if (!activityLevel.value) return 0;

  const multipliers: Record<string, number> = {
    low: 1.2,
    moderate: 1.55,
    high: 1.725,
  };

  return Math.round(bmr.value * (multipliers[activityLevel.value] || 1.55));
});

// Apply goal adjustment
const dailyTarget = computed(() => {
  if (!goal.value) return 0;

  const adjustments: Record<string, number> = {
    lose: -400,
    maintain: 0,
    gain: 400,
  };

  return Math.round(tdee.value + (adjustments[goal.value] || 0));
});

// Store calorie estimates for each meal
const _mealCalories = reactive<Record<string, Record<string, number>>>({
  monday: { breakfast: 0, lunch: 0, dinner: 0 },
  tuesday: { breakfast: 0, lunch: 0, dinner: 0 },
  wednesday: { breakfast: 0, lunch: 0, dinner: 0 },
  thursday: { breakfast: 0, lunch: 0, dinner: 0 },
  friday: { breakfast: 0, lunch: 0, dinner: 0 },
  saturday: { breakfast: 0, lunch: 0, dinner: 0 },
  sunday: { breakfast: 0, lunch: 0, dinner: 0 },
});

// Week plan initial structure
function emptyMealDay(): MealDay {
  return { breakfast: null, lunch: null, dinner: null };
}

const weekPlan = reactive<WeekPlan>({
  monday: emptyMealDay(),
  tuesday: emptyMealDay(),
  wednesday: emptyMealDay(),
  thursday: emptyMealDay(),
  friday: emptyMealDay(),
  saturday: emptyMealDay(),
  sunday: emptyMealDay(),
});

// Helpers
function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Load from localStorage on mount
onMounted(() => {
  try {
    // Ensure recipe list is loaded (frontend-only call if not present)
    if (!allRecipes.value?.length) {
      // call useRecipes to trigger fetching all recipes
      const { getAllRecipes } = useRecipes(true, true);
      // getAllRecipes is already called by useRecipes when fetchRecipes=true,
      // but call it defensively if still empty
      getAllRecipes?.();
    }

    // Load user metrics
    const rawWeight = localStorage.getItem("dietPlannerWeight");
    if (rawWeight) {
      const parsed = parseFloat(rawWeight);
      if (!isNaN(parsed)) weight.value = parsed;
    }

    const rawHeight = localStorage.getItem("dietPlannerHeight");
    if (rawHeight) {
      const parsed = parseFloat(rawHeight);
      if (!isNaN(parsed)) height.value = parsed;
    }

    const rawAge = localStorage.getItem("dietPlannerAge");
    if (rawAge) {
      const parsed = parseInt(rawAge, 10);
      if (!isNaN(parsed)) age.value = parsed;
    }

    const rawGender = localStorage.getItem("dietPlannerGender");
    if (rawGender && (rawGender === "male" || rawGender === "female")) {
      gender.value = rawGender;
    }

    const rawActivity = localStorage.getItem("dietPlannerActivity");
    if (rawActivity && (rawActivity === "low" || rawActivity === "moderate" || rawActivity === "high")) {
      activityLevel.value = rawActivity;
    }

    const rawGoal = localStorage.getItem("dietPlannerGoal");
    if (rawGoal) {
      // Validate
      if (rawGoal === "lose" || rawGoal === "maintain" || rawGoal === "gain") {
        goal.value = rawGoal as Goal;
      }
    }

    const rawWeek = localStorage.getItem("dietPlannerWeekPlan");
    if (rawWeek) {
      const parsed = JSON.parse(rawWeek) as Partial<WeekPlan> | null;
      if (parsed && typeof parsed === "object") {
        for (const d of days) {
          const dayObj = (parsed as any)[d];
          if (dayObj && typeof dayObj === "object") {
            weekPlan[d].breakfast = dayObj.breakfast ?? null;
            weekPlan[d].lunch = dayObj.lunch ?? null;
            weekPlan[d].dinner = dayObj.dinner ?? null;
          }
        }
      }
    }
  }
  catch {
    // ignore JSON parse errors and continue with defaults
  }

  // Set up periodic refresh of recipes (every 10 seconds) to catch new recipes
  const recipeRefreshInterval = setInterval(async () => {
    try {
      const { getAllRecipes } = useRecipes(true, true);
      getAllRecipes?.();
    }
    catch (error) {
      console.warn("[DietPlanner] Error refreshing recipes:", error);
    }
  }, 10000); // Refresh every 10 seconds

  // Cleanup interval on component unmount
  onBeforeUnmount(() => {
    clearInterval(recipeRefreshInterval);
  });
});

// Watch for changes to allRecipes and refresh dropdown
watch(
  () => allRecipes.value,
  () => {
    // Log to confirm recipes were updated
    console.log(`[DietPlanner] Recipes updated, total count: ${allRecipes.value?.length || 0}`);
  },
);

// Watch for changes to weekPlan and update calorie estimates
watch(
  () => weekPlan,
  async () => {
    // Recalculate calories for all meals when selections change
    for (const day of days) {
      _mealCalories[day].breakfast = await _fetchAndCacheMealCalories(day, "breakfast");
      _mealCalories[day].lunch = await _fetchAndCacheMealCalories(day, "lunch");
      _mealCalories[day].dinner = await _fetchAndCacheMealCalories(day, "dinner");
    }
    // Also save to localStorage
    localStorage.setItem(STORAGE_WEEK_KEY, JSON.stringify(weekPlan));
  },
  { deep: true },
);

// Helper to lookup recipe by id from the store
function _getRecipeById(id: string | null | undefined) {
  if (!id) return null;
  // Debug: log to help identify mismatch
  const found = recipes.value?.find((r: any) => r.id === id);
  if (!found && recipes.value && recipes.value.length > 0) {
    console.warn(`[DietPlanner] Recipe not found for id: ${id}, available count:`, recipes.value.length);
  }
  return found ?? null;
}

// Async function to fetch full recipe and cache it, returning calorie estimate
async function _fetchAndCacheMealCalories(day: keyof typeof weekPlan, mealKey: keyof MealDay): Promise<number> {
  const id = weekPlan[day][mealKey];
  if (!id) return 0;

  // Check cache first
  if (_fullRecipeCache.value.has(id as string)) {
    const cachedRecipe = _fullRecipeCache.value.get(id as string);
    const calories = estimateRecipeCalories(cachedRecipe);
    console.log(`[DietPlanner] Using cached recipe for ${id}, calories: ${calories}`);
    return calories;
  }

  // Find recipe in summary list to get slug
  let recipeSlug: string | null = null;
  let recipe = _getRecipeById(id as string);

  if (!recipe && recipes.value && recipes.value.length > 0) {
    const found = recipes.value.find((r: any) => String(r.id).trim() === String(id).trim());
    recipe = found ?? null;
  }

  if (recipe?.slug) {
    recipeSlug = recipe.slug;
  }

  // If no slug found, cannot fetch full recipe - return 0
  if (!recipeSlug) {
    console.warn(`[DietPlanner] Recipe slug not found for id: ${id}`);
    return 0;
  }

  try {
    // Fetch full recipe with ingredients
    console.log(`[DietPlanner] Fetching full recipe data for slug: ${recipeSlug}`);
    const { data: fullRecipe } = await _api.recipes.getOne(recipeSlug);

    if (fullRecipe) {
      // Cache the full recipe
      _fullRecipeCache.value.set(id as string, fullRecipe);
      const calories = estimateRecipeCalories(fullRecipe);
      console.log(`[DietPlanner] Recipe ${recipeSlug} fetched, calories: ${calories}, ingredients: ${fullRecipe.recipeIngredient?.length || 0}`);
      return calories;
    }
  }
  catch (error) {
    console.error(`[DietPlanner] Failed to fetch recipe ${recipeSlug}:`, error);
  }

  // Fallback to summary recipe if fetch failed
  const fallbackCalories = recipe ? estimateRecipeCalories(recipe) : 0;
  console.log(`[DietPlanner] Fallback to summary recipe for ${id}, calories: ${fallbackCalories}`);
  return fallbackCalories;
}

// Ingredient-based calorie estimator
function estimateRecipeCalories(recipe: any) {
  if (!recipe) return 0;

  // Handle Mealie's recipeIngredient format (array of objects)
  const ingredients = recipe.recipeIngredient || recipe.ingredients || [];
  if (!Array.isArray(ingredients) || ingredients.length === 0) {
    // Fallback: try to estimate from recipe name if no ingredients loaded
    if (recipe.name) {
      const name = String(recipe.name).toLowerCase();
      if (name.includes("chicken")) return 200;
      if (name.includes("fish") || name.includes("salmon")) return 180;
      if (name.includes("rice")) return 150;
    }
    return 0;
  }

  let total = 0;

  const rules: Array<{ keys: string[]; cal: number }> = [
    { keys: ["chicken"], cal: 200 },
    { keys: ["fish", "salmon", "tuna"], cal: 180 },
    { keys: ["mutton", "lamb"], cal: 250 },
    { keys: ["paneer"], cal: 220 },
    { keys: ["tofu"], cal: 150 },
    { keys: ["egg", "eggs"], cal: 70 },
    { keys: ["dal", "lentil", "lentils"], cal: 140 },
    { keys: ["chickpea", "chickpeas", "chana"], cal: 150 },

    { keys: ["rice"], cal: 150 },
    { keys: ["bread"], cal: 80 },
    { keys: ["roti", "chapati"], cal: 100 },
    { keys: ["noodle", "noodles"], cal: 160 },
    { keys: ["pasta"], cal: 170 },
    { keys: ["potato"], cal: 90 },
    { keys: ["corn"], cal: 120 },
    { keys: ["oat", "oats"], cal: 130 },

    { keys: ["oil", "olive oil", "coconut oil"], cal: 120 },
    { keys: ["butter"], cal: 120 },
    { keys: ["ghee"], cal: 130 },
    { keys: ["cheese"], cal: 110 },
    { keys: ["cream"], cal: 100 },

    { keys: ["onion"], cal: 30 },
    { keys: ["tomato"], cal: 25 },
    { keys: ["carrot"], cal: 35 },
    { keys: ["bean", "beans"], cal: 30 },
    { keys: ["cabbage"], cal: 25 },
    { keys: ["cauliflower"], cal: 25 },
    { keys: ["spinach"], cal: 20 },
    { keys: ["capsicum", "pepper"], cal: 25 },
    { keys: ["pea", "peas"], cal: 40 },

    { keys: ["milk"], cal: 50 },
    { keys: ["curd", "yogurt", "yoghurt"], cal: 60 },

    { keys: ["sugar"], cal: 40 },
    { keys: ["jaggery"], cal: 50 },
    { keys: ["honey"], cal: 45 },
  ];

  for (const ing of ingredients) {
    if (!ing) continue;

    // Extract ingredient name from Mealie's RecipeIngredient format
    // Try: food.name, display, originalText, or title
    let ingredientName = "";
    if (ing.food?.name) {
      ingredientName = ing.food.name;
    }
    else if (ing.display) {
      ingredientName = ing.display;
    }
    else if (ing.originalText) {
      ingredientName = ing.originalText;
    }
    else if (ing.title) {
      ingredientName = ing.title;
    }
    else if (typeof ing === "string") {
      ingredientName = ing;
    }

    if (!ingredientName) continue;

    const s = String(ingredientName).toLowerCase();
    let matched = false;
    for (const rule of rules) {
      for (const k of rule.keys) {
        if (s.includes(k)) {
          total += rule.cal;
          matched = true;
          break;
        }
      }
      if (matched) break;
    }
    if (!matched) {
      total += 40; // default for unknown ingredient
    }
  }

  return total;
}

function getDayCalories(day: keyof typeof weekPlan) {
  return _mealCalories[day].breakfast
    + _mealCalories[day].lunch
    + _mealCalories[day].dinner;
}

// Helper to get the text showing comparison vs daily target
function getDayTargetText(day: keyof typeof weekPlan): string {
  const dayTotal = getDayCalories(day);
  const target = dailyTarget.value;
  const diff = dayTotal - target;

  if (diff === 0) {
    return "On target";
  }
  if (diff > 0) {
    return `Over by: ${diff} kcal`;
  }
  return `Remaining: ${Math.abs(diff)} kcal`;
}

// Helper to get CSS class for target comparison color
function getDayTargetClass(day: keyof typeof weekPlan): string {
  const dayTotal = getDayCalories(day);
  const target = dailyTarget.value;
  const diff = dayTotal - target;

  if (diff === 0) {
    return ""; // neutral
  }
  if (diff > 0) {
    return "error--text"; // red for over
  }
  return "success--text"; // green for under
}

const _weeklyTotal = computed(() => {
  return days.reduce((acc, d) => acc + getDayCalories(d as keyof typeof weekPlan), 0);
});

const averagePerDay = computed(() => {
  return Math.round(_weeklyTotal.value / days.length);
});

const daysOverTarget = computed(() => {
  return days.filter((d) => {
    const dayTotal = getDayCalories(d as keyof typeof weekPlan);
    return dayTotal > dailyTarget.value;
  }).length;
});

const daysUnderTarget = computed(() => {
  return days.filter((d) => {
    const dayTotal = getDayCalories(d as keyof typeof weekPlan);
    return dayTotal < dailyTarget.value;
  }).length;
});

// Helper to count recipes containing specific ingredients
function countRecipesWithIngredient(ingredientKeys: string[]): number {
  let count = 0;
  const checkedRecipes = new Set<string>();

  for (const day of days) {
    const mealIds = [
      weekPlan[day].breakfast,
      weekPlan[day].lunch,
      weekPlan[day].dinner,
    ].filter(Boolean);

    for (const id of mealIds) {
      if (!id || checkedRecipes.has(id)) continue;
      checkedRecipes.add(id);

      const recipe = _getRecipeById(id as string);
      if (!recipe) continue;

      const cachedRecipe = _fullRecipeCache.value.get(id as string);
      const ingredients = cachedRecipe?.recipeIngredient || recipe.recipeIngredient || [];

      for (const ing of ingredients) {
        let ingredientName = "";
        if (ing.food?.name) {
          ingredientName = ing.food.name;
        }
        else if (ing.display) {
          ingredientName = ing.display;
        }
        else if (ing.originalText) {
          ingredientName = ing.originalText;
        }
        else if (ing.title) {
          ingredientName = ing.title;
        }
        else if (typeof ing === "string") {
          ingredientName = ing;
        }

        if (!ingredientName) continue;

        const s = String(ingredientName).toLowerCase();
        for (const key of ingredientKeys) {
          if (s.includes(key)) {
            count++;
            break;
          }
        }
      }
    }
  }

  return count;
}

// Compute health suggestions based on weekly results and user's goal
const healthSuggestions = computed(() => {
  const suggestions: string[] = [];
  const avgCalories = averagePerDay.value;
  const target = dailyTarget.value;
  const surplus = avgCalories - target;

  // If no meals planned yet
  if (
    days.every((d) => {
      const meals = [weekPlan[d].breakfast, weekPlan[d].lunch, weekPlan[d].dinner];
      return meals.every(m => !m);
    })
  ) {
    return [];
  }

  // Count recipes with vegetables
  const vegCount = countRecipesWithIngredient([
    "spinach",
    "broccoli",
    "carrot",
    "tomato",
    "capsicum",
    "pepper",
    "cabbage",
    "cauliflower",
    "bean",
    "beans",
  ]);

  // Count recipes with proteins
  const proteinCount = countRecipesWithIngredient([
    "chicken",
    "fish",
    "mutton",
    "lamb",
    "paneer",
    "tofu",
    "egg",
    "eggs",
    "dal",
    "lentil",
    "lentils",
    "chickpea",
    "chickpeas",
    "chana",
  ]);

  // Count recipes with oils/butters/fried
  const fatCount = countRecipesWithIngredient([
    "oil",
    "butter",
    "ghee",
    "fried",
    "cream",
  ]);

  // Goal-specific suggestions
  if (goal.value === "maintain") {
    if (daysOverTarget.value === 7) {
      suggestions.push(`🎯 Critical: All 7 days are over target by an average of ${Math.round(surplus)} kcal. To maintain your weight, reduce portion sizes by 15-20% or decrease oil/butter usage by 30%.`);
    }
    else if (daysOverTarget.value >= 5) {
      suggestions.push(`⚠️ High Surplus: ${daysOverTarget.value} days over target. Average daily surplus: ${Math.round(surplus)} kcal. Consider reducing daily calorie intake by 200-300 kcal to stay consistent.`);
    }
    else if (daysOverTarget.value >= 3) {
      suggestions.push(`📊 Moderate Surplus: ${daysOverTarget.value} days over target. Try reducing portion sizes of high-calorie foods (oils, ghee, cream) by 20%.`);
    }
    else if (daysOverTarget.value === 0 && daysUnderTarget.value === 0) {
      suggestions.push("✅ Perfect! Your meals are perfectly aligned with maintenance calories. Keep this balance consistent.");
    }
  }
  else if (goal.value === "lose") {
    if (daysOverTarget.value === 7) {
      suggestions.push(`🎯 Important: All days are over your weight loss target. You need a deficit of 400 kcal/day. Currently averaging +${Math.round(surplus)} kcal. Reduce portions by 25-30%.`);
    }
    else if (daysOverTarget.value >= 5) {
      suggestions.push(`⚠️ Most days exceed target. To achieve weight loss, you need to create a 400 kcal daily deficit. Replace fried foods with grilled alternatives.`);
    }
    else if (daysOverTarget.value >= 2) {
      suggestions.push("📈 Some days exceed target. Cut back on oil usage and add more vegetables to increase satiety with fewer calories.");
    }
    else if (daysUnderTarget.value >= 4) {
      suggestions.push("✅ Excellent! You're on track for healthy weight loss. Maintain this caloric deficit consistently.");
    }
  }
  else if (goal.value === "gain") {
    if (daysUnderTarget.value >= 5) {
      suggestions.push(`📉 Deficit Detected: ${daysUnderTarget.value} days under target. You need +400 kcal surplus to gain. Add calorie-dense foods like nuts, whole milk, and olive oil to meals.`);
    }
    else if (daysUnderTarget.value >= 2) {
      suggestions.push("⬆️ Add 200-300 kcal daily. Include healthy fats (nuts, seeds), whole milk products, and protein with every meal to support muscle gain.");
    }
    else if (daysOverTarget.value >= 4) {
      suggestions.push("✅ Perfect! You're in a caloric surplus for healthy weight gain. Ensure adequate protein for muscle building.");
    }
  }

  // Protein suggestions
  if (proteinCount >= 5) {
    if (goal.value === "lose") {
      suggestions.push("💪 Excellent protein intake! This helps preserve muscle during weight loss. Maintain this consistency.");
    }
    else if (goal.value === "gain") {
      suggestions.push("💪 Strong protein choices! Combined with your caloric surplus, this supports effective muscle gain.");
    }
    else {
      suggestions.push("💪 Great protein diversity! This supports satiety and stable metabolism for weight maintenance.");
    }
  }
  else if (proteinCount <= 2) {
    suggestions.push("🥩 Increase protein intake. Add more chicken, fish, eggs, or legumes to every meal to support your goal and keep you fuller longer.");
  }

  // Vegetable suggestions
  if (vegCount >= 4) {
    suggestions.push("🥗 Outstanding! High vegetable intake ensures fiber, micronutrients, and helps with satiety without excess calories.");
  }
  else if (vegCount >= 2) {
    suggestions.push("🥬 Add more vegetables. They provide fiber to stay full longer, essential for all fitness goals.");
  }
  else if (vegCount === 0 && daysOverTarget.value > 0) {
    suggestions.push("🥕 Critical: Add vegetables to EVERY meal. They'll help you feel full with fewer calories while hitting nutritional targets.");
  }

  // Fat/Oil suggestions
  if (fatCount >= 5) {
    if (goal.value === "maintain" && daysOverTarget.value >= 4) {
      suggestions.push("🛢️ High fat usage detected. Reduce oils/ghee by 30-40%. Use cooking spray or non-stick pans. Grill or steam instead of frying.");
    }
    else if (goal.value === "lose") {
      suggestions.push("🛢️ High fat content. Reduce oil/butter by 25-30%. Use healthier cooking methods like grilling, baking, or steaming.");
    }
    else if (goal.value === "gain" && daysUnderTarget.value >= 2) {
      suggestions.push("🛢️ Good! Healthy fats help reach your calorie surplus. Maintain oils but balance with whole foods like nuts and avocados.");
    }
  }
  else if (fatCount <= 1 && goal.value === "gain") {
    suggestions.push("🥑 Add healthy fats. Use oils, nuts, seeds, and ghee to increase calories for weight gain while maintaining nutrition.");
  }

  // Practical lifestyle tips based on goal
  if (goal.value === "maintain") {
    suggestions.push("🏃 For weight maintenance: Stay consistent with these calorie levels and exercise 3-4 times weekly for health benefits.");
  }
  else if (goal.value === "lose") {
    suggestions.push("🏃 For weight loss: Pair your calorie deficit with 150+ minutes of cardio weekly and 2-3 strength sessions for optimal results.");
  }
  else if (goal.value === "gain") {
    suggestions.push("💪 For weight gain: Focus on strength training 4-5 times weekly. This ensures the surplus becomes muscle, not just fat.");
  }

  return suggestions;
});

// Persist user metrics and goal
watch(weight, (val) => {
  try {
    if (val === null) {
      localStorage.removeItem("dietPlannerWeight");
    }
    else {
      localStorage.setItem("dietPlannerWeight", String(val));
    }
  }
  catch {
    // ignore storage errors
  }
});

watch(height, (val) => {
  try {
    if (val === null) {
      localStorage.removeItem("dietPlannerHeight");
    }
    else {
      localStorage.setItem("dietPlannerHeight", String(val));
    }
  }
  catch {
    // ignore storage errors
  }
});

watch(age, (val) => {
  try {
    if (val === null) {
      localStorage.removeItem("dietPlannerAge");
    }
    else {
      localStorage.setItem("dietPlannerAge", String(val));
    }
  }
  catch {
    // ignore storage errors
  }
});

watch(gender, (val) => {
  try {
    if (val === null) {
      localStorage.removeItem("dietPlannerGender");
    }
    else {
      localStorage.setItem("dietPlannerGender", val);
    }
  }
  catch {
    // ignore storage errors
  }
});

watch(activityLevel, (val) => {
  try {
    localStorage.setItem("dietPlannerActivity", val);
  }
  catch {
    // ignore storage errors
  }
});

watch(goal, (val) => {
  try {
    if (val === null) {
      localStorage.removeItem("dietPlannerGoal");
    }
    else {
      localStorage.setItem("dietPlannerGoal", val);
    }
  }
  catch {
    // ignore storage errors
  }
});

watch(
  () => weekPlan,
  (newVal) => {
    try {
      localStorage.setItem("dietPlannerWeekPlan", JSON.stringify(newVal));
    }
    catch {
      // ignore storage errors
    }
  },
  { deep: true },
);
</script>

<style scoped>
/* Minimal styling; Vuetify + theme provides the main look */
</style>
