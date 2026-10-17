<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1" />
      <v-card-text v-if="edit">
        <div
          v-for="(item, key, index) in modelValue"
          :key="index"
        >
          <v-number-input
            :model-value="parseNutritionValue(modelValue[key])"
            :label="labels[key].label"
            :suffix="labels[key].suffix"
            density="compact"
            autocomplete="off"
            variant="underlined"
            inset
            :precision="null"
            :min="0"
            @update:model-value="updateValue(key, $event)"
          />
        </div>
      </v-card-text>
      <div
        v-if="showViewer"
        class="nutrition-list px-4 pb-2"
      >
        <v-switch
          v-if="weightEstimate.matched > 0"
          v-model="autoCalculate"
          :label="$t('recipe.nutrition-auto-calculate')"
          density="compact"
          color="primary"
          hide-details
          class="mb-1"
        />
        <div
          v-for="(item, key, index) in primaryList"
          :key="`primary-${index}`"
          class="nutrition-row"
        >
          <span>{{ item.label }}</span>
          <span class="font-weight-medium">{{ item.value }} {{ item.suffix }}</span>
        </div>
        <v-expand-transition>
          <div v-if="showSecondary">
            <div
              v-for="(item, key, index) in secondaryList"
              :key="`secondary-${index}`"
              class="nutrition-row"
            >
              <span>{{ item.label }}</span>
              <span class="font-weight-medium">{{ item.value }} {{ item.suffix }}</span>
            </div>
          </div>
        </v-expand-transition>
        <v-btn
          v-if="hasSecondaryValues"
          variant="text"
          density="compact"
          class="px-0 mt-1 text-none"
          @click="showSecondary = !showSecondary"
        >
          {{ showSecondary ? $t("recipe.nutrition-less-details") : $t("recipe.nutrition-more-details") }}
        </v-btn>
        <div
          v-if="autoCalculate"
          class="text-caption text-medium-emphasis mt-2"
        >
          {{ $t('recipe.nutrition-auto-calculate-hint', {
            matched: weightEstimate.matched,
            total: weightEstimate.total,
            weight: weightEstimate.grams.toFixed(0),
            perServing: weightPerServing.toFixed(0),
          }) }}
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { estimateNutritionPer100g, estimateRecipeWeightGrams, parseNutritionValue, useNutritionLabels } from "~/composables/recipes";
import type { Nutrition, RecipeIngredient } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";

// The four macros shown up front, matching how most nutrition labels are read at a glance.
// Everything else in the schema is secondary and hidden behind "more details".
const PRIMARY_KEYS = ["calories", "proteinContent", "carbohydrateContent", "fatContent"];

interface Props {
  edit?: boolean;
  ingredients?: RecipeIngredient[];
  servings?: number;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
  ingredients: () => [],
  servings: 1,
});

const modelValue = defineModel<Nutrition>({ required: true });

const { labels } = useNutritionLabels();
const valueNotNull = computed(() => {
  let key: keyof Nutrition;
  for (key in modelValue.value) {
    if (modelValue.value[key] !== null) {
      return true;
    }
  }
  return false;
});

const showViewer = computed(() => !props.edit && valueNotNull.value);
const showSecondary = ref(false);
const autoCalculate = ref(false);

function updateValue(key: number | string, value: number | null) {
  modelValue.value = { ...modelValue.value, [key]: value?.toString() ?? null };
}

// The nutrition values entered on a recipe are per serving - estimating a recipe's weight from
// its ingredients gives the whole recipe's weight, so it's divided by the serving count here.
const weightEstimate = computed(() => estimateRecipeWeightGrams(props.ingredients));
const weightPerServing = computed(() => weightEstimate.value.grams / (props.servings || 1));

const displayedNutrition = computed(() => {
  if (!autoCalculate.value) {
    return modelValue.value;
  }
  return estimateNutritionPer100g(modelValue.value, weightPerServing.value);
});

// Build a new list that only contains nutritional information that has a value
const renderedList = computed(() => {
  return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
    if (displayedNutrition.value[key]?.trim()) {
      item[key] = {
        ...label,
        value: displayedNutrition.value[key],
      };
    }
    return item;
  }, {});
});

const primaryList = computed(() => {
  return PRIMARY_KEYS.reduce((item: NutritionLabelType, key) => {
    if (renderedList.value[key]) {
      item[key] = renderedList.value[key];
    }
    return item;
  }, {});
});

const secondaryList = computed(() => {
  return Object.entries(renderedList.value).reduce((item: NutritionLabelType, [key, label]) => {
    if (!PRIMARY_KEYS.includes(key)) {
      item[key] = label;
    }
    return item;
  }, {});
});

const hasSecondaryValues = computed(() => Object.keys(secondaryList.value).length > 0);
</script>

<style lang="scss" scoped>
.nutrition-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  min-height: 36px;
  padding-top: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));

  &:last-of-type {
    border-bottom: none;
  }
}
</style>
