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
          <v-text-field
            :model-value="recipeServings"
            type="number"
            :min="0"
            hide-spin-buttons
            density="compact"
            :label="$t('recipe.servings')"
            variant="underlined"
            @update:model-value="validateInput($event, 'recipeServings')"
          />
        </v-col>
        <v-col cols="3">
          <v-text-field
            :model-value="recipeYieldQuantity"
            type="number"
            :min="0"
            hide-spin-buttons
            density="compact"
            :label="$t('recipe.yield')"
            variant="underlined"
            @update:model-value="validateInput($event, 'recipeYieldQuantity')"
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

    <div
      class="d-flex flex-wrap"
      style="gap: 1rem"
    >
      <v-text-field
        v-model="recipe.totalTime"
        :label="$t('recipe.total-time')"
        density="compact"
        variant="underlined"
      />
      <v-text-field
        v-model="recipe.prepTime"
        :label="$t('recipe.prep-time')"
        density="compact"
        variant="underlined"
      />
      <v-text-field
        v-model="recipe.performTime"
        :label="$t('recipe.perform-time')"
        density="compact"
        variant="underlined"
      />
    </div>
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
import { validators } from "~/composables/use-validators";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });

const recipeServings = computed<number>({
  get() {
    return recipe.value.recipeServings;
  },
  set(val) {
    validateInput(val.toString(), "recipeServings");
  },
});

const recipeYieldQuantity = computed<number>({
  get() {
    return recipe.value.recipeYieldQuantity;
  },
  set(val) {
    validateInput(val.toString(), "recipeYieldQuantity");
  },
});

function validateInput(value: string | null, property: "recipeServings" | "recipeYieldQuantity") {
  if (!value) {
    recipe.value[property] = 0;
    return;
  }

  const number = parseFloat(value.replace(/[^0-9.]/g, ""));
  if (isNaN(number) || number <= 0) {
    recipe.value[property] = 0;
    return;
  }

  recipe.value[property] = number;
}
</script>
