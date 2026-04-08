<template>
  <div v-if="showSection">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1" />

      <!-- Manual nutrition: editable fields or viewer -->
      <v-card-text v-if="edit">
        <div
          v-for="(item, key, index) in modelValue"
          :key="index"
        >
          <v-number-input
            :model-value="modelValue[key]"
            :label="labels[key].label"
            :suffix="labels[key].suffix"
            density="compact"
            autocomplete="off"
            variant="underlined"
            control-variant="stacked"
            inset
            :precision="null"
            :min="0"
            @update:model-value="updateValue(key, $event)"
          />
        </div>
      </v-card-text>
      <v-list
        v-if="showManualViewer"
        density="compact"
        class="mt-0 pt-0"
      >
        <v-list-item
          v-for="(item, key, index) in renderedManualList"
          :key="index"
          style="min-height: 25px"
        >
          <v-list-item-title class="pl-2 d-flex">
            <div>{{ item.label }}</div>
            <div class="ml-auto mr-1">
              {{ item.value }}
            </div>
            <div>{{ item.suffix }}</div>
          </v-list-item-title>
        </v-list-item>
      </v-list>

      <!-- Calculated nutrition (read-only) -->
      <template v-if="showCalculated">
        <v-divider
          v-if="showManualViewer || edit"
          class="mx-2 my-1"
        />
        <v-card-subtitle class="px-4 pt-2 pb-0 text-medium-emphasis">
          {{ $t("nutrition.calculated-from-ingredients") }}
        </v-card-subtitle>
        <v-list
          density="compact"
          class="mt-0 pt-0"
        >
          <v-list-item
            v-for="(item, key, index) in renderedCalculatedList"
            :key="index"
            style="min-height: 25px"
          >
            <v-list-item-title class="pl-2 d-flex">
              <div>{{ item.label }}</div>
              <div class="ml-auto mr-1">
                {{ item.value }}
              </div>
              <div>{{ item.suffix }}</div>
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </template>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes";
import type { Nutrition } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";

interface Props {
  edit?: boolean;
  calculatedNutrition?: Nutrition | null;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
  calculatedNutrition: null,
});

const modelValue = defineModel<Nutrition>({ required: true });

const { labels } = useNutritionLabels();

function hasValue(nutrition: Nutrition | null | undefined): boolean {
  if (!nutrition) return false;
  let key: keyof Nutrition;
  for (key in nutrition) {
    if (nutrition[key] !== null && nutrition[key] !== undefined) {
      return true;
    }
  }
  return false;
}

const manualNotNull = computed(() => hasValue(modelValue.value));
const showManualViewer = computed(() => !props.edit && manualNotNull.value);
const showCalculated = computed(() => hasValue(props.calculatedNutrition));
const showSection = computed(() => props.edit || manualNotNull.value || showCalculated.value);

function updateValue(key: number | string, event: Event) {
  modelValue.value = { ...modelValue.value, [key]: event };
}

function buildRenderedList(nutrition: Nutrition | null | undefined): NutritionLabelType {
  if (!nutrition) return {};
  return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
    const val = nutrition[key as keyof Nutrition];
    if (val?.trim()) {
      item[key] = { ...label, value: val };
    }
    return item;
  }, {});
}

const renderedManualList = computed(() => buildRenderedList(modelValue.value));
const renderedCalculatedList = computed(() => buildRenderedList(props.calculatedNutrition));
</script>

<style lang="scss" scoped></style>
