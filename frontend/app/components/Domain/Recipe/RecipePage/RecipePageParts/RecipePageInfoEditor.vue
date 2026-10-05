<template>
  <div>
    <v-text-field
      v-model="recipe.name"
      class="my-3"
      :label="$t('recipe.recipe-name')"
      :rules="[validators.required]"
      density="compact"
      variant="underlined"
    />
    <v-container class="ma-0 pa-0">
      <v-row>
        <v-col cols="3">
          <v-number-input
            :model-value="recipe.recipeServings"
            :min="0"
            :precision="null"
            density="compact"
            :label="$t('recipe.servings')"
            variant="underlined"
            control-variant="hidden"
            @update:model-value="recipe.recipeServings = $event"
          />
        </v-col>
        <v-col cols="3">
          <v-number-input
            :model-value="recipe.recipeYieldQuantity"
            :min="0"
            :precision="null"
            density="compact"
            :label="$t('recipe.yield')"
            variant="underlined"
            control-variant="hidden"
            @update:model-value="recipe.recipeYieldQuantity = $event"
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="recipe.recipeYield"
            density="compact"
            :label="$t('recipe.yield-text')"
            variant="underlined"
          />
        </v-col>
      </v-row>
    </v-container>

    <RecipeTimeInput
      v-model:seconds="recipe.totalTimeSeconds"
      v-model:text="recipe.totalTime"
      :label="$t('recipe.total-time')"
    />
    <RecipeTimeInput
      v-model:seconds="recipe.prepTimeSeconds"
      v-model:text="recipe.prepTime"
      :label="$t('recipe.prep-time')"
    />
    <RecipeTimeInput
      v-model:seconds="recipe.performTimeSeconds"
      v-model:text="recipe.performTime"
      :label="$t('recipe.perform-time')"
    />
    <v-textarea
      v-model="recipe.description"
      auto-grow
      min-height="100"
      :label="$t('recipe.description')"
      density="compact"
      variant="underlined"
    />
  </div>
</template>

<script setup lang="ts">
import RecipeTimeInput from "~/components/Domain/Recipe/RecipeTimeInput.vue";
import { validators } from "~/composables/use-validators";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
</script>
