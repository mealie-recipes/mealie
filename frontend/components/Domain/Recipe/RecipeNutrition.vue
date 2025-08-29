<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title v-if="showViewer && !useTableView"
      class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1" />
      <v-card-text v-if="edit">
        <div
          v-for="(item, key, index) in modelValue"
          :key="index"
        >
          <v-text-field
            density="compact"
            :model-value="modelValue[key]"
            :label="labels[key].label"
            :suffix="labels[key].suffix"
            type="number"
            autocomplete="off"
            variant="underlined"
            @update:model-value="updateValue(key, $event)"
          />
        </div>
      </v-card-text>
      <!-- Classic List View -->
      <v-list
        v-if="showViewer && !useTableView"
        density="compact"
        class="mt-0 pt-0"
      >
        <v-list-item
          v-for="(item, key, index) in renderedList"
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
      <!-- Nutrition Information Table Format -->
       <v-table
          v-if="showViewer && useTableView"
          class="mt-0 pt-0 nutrition-table"
        >
        <thead>
          <tr>
            <th colspan="3" style="text-align: center;">
              NUTRITION INFORMATION
            </th>
          </tr>
          <tr>
            <th />
            <th>Quantity per serving</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(nutrient, index) in nutrients" :key="index">
            <td :class="{ 'pl-8': nutrient.indent }">
              {{ nutrient.label }}
            </td>
            <td class="pl-8 d-flex align-center">
              <template v-if="nutrient.special">
                <div class="mr-4">
                  <span>
                   {{ energyValue }}
                  </span>
                </div>
                <v-switch
                  v-model="showInKcal"
                  color="primary"
                  hide-details
                  class="ml-auto"
                  :label="showInKcal ? 'kcal' : 'kJ'"
                />
              </template>

              <!-- Default -->
              <template v-else>
                {{ nutrient.value || '-' }} {{ nutrient.unit }}
              </template>
            </td>
          </tr>
        </tbody>
      </v-table>
      <v-switch
          v-if="showViewer"
          v-model="useTableView"
          hide-details
          color="primary"
          class="ml-auto"
          :label="useTableView ? 'Table view' : 'List view'"
        />
    </v-card>
</div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes";
import type { Nutrition } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";

interface Props {
  edit?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  edit: true,
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

function updateValue(key: number | string, event: Event) {
  modelValue.value = { ...modelValue.value, [key]: event };
}

// Build a new list that only contains nutritional information that has a value
const renderedList = computed(() => {
  return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
    if (modelValue.value[key]?.trim()) {
      item[key] = {
        ...label,
        value: modelValue.value[key],
      };
    }
    return item;
  }, {});
});

// Build nutrition information table format
const useTableView = ref(true);

const showInKcal = ref(true);

const nutrients = computed(() => [
  { label: "Energy", value: modelValue.value.calories, unit: "", special: true },
  { label: "Protein", value: modelValue.value.proteinContent, unit: "g" },
  { label: "Fat, total", value: modelValue.value.fatContent, unit: "g" },
  { label: "– Saturated", value: modelValue.value.saturatedFatContent, unit: "g", indent: true },
  { label: "Carbohydrate", value: modelValue.value.carbohydrateContent, unit: "g" },
  { label: "– Sugars", value: modelValue.value.sugarContent, unit: "g", indent: true },
  { label: "Dietary Fibre", value: modelValue.value.fiberContent, unit: "g" },
  { label: "Sodium", value: modelValue.value.sodiumContent, unit: "mg" },
]);

const energyValue = computed(() => {
  if (!modelValue.value.calories) return "-";
  return showInKcal.value
    ? `${modelValue.value.calories} kcal`
    : `${(Number(modelValue.value.calories) * 4.184).toFixed(0)} kJ`;
});
</script>

<style lang="scss" scoped>

</style>
