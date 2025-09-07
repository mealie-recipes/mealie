<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title
        v-if="showViewer"
        class="pt-2 pb-0"
      >
        {{ $t("recipe.nutrition") }}
      </v-card-title>

      <v-divider class="mx-2 my-1" />

      <!-- Edit mode -->
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
      <div v-if="showViewer && useTableView" class="overflow-x-hidden">
        <v-table density="compact">
          <thead>
            <tr>
              <th />
              <th class="text-end">
Quantity per serving
</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(nutrient, index) in nutrients" :key="index">
              <td :class="{ 'pl-8': nutrient.indent }" style="width: 150px;">
                {{ nutrient.label }}
              </td>
              <td class="ml-auto mr-1 text-right">
                <template v-if="nutrient.special">
                  <div>
                    <span v-if="calView">
                      {{ modelValue?.calories || '-' }} kcal
                    </span>
                    <span v-else>
                      {{ modelValue?.calories ? (Number(modelValue.calories) * 4.184).toFixed(0) : '-' }} kJ
                    </span>
                  </div>
                </template>
                <template v-else>
                  {{ nutrient.value || '-' }} {{ nutrient.unit }}
                </template>
              </td>
            </tr>
          </tbody>
        </v-table>
      </div>
      <!-- Toggle View -->
        <div>
          <v-switch
            v-model="useTableView"
            class="pl-8"
            hide-details
            density="compact"
            :label="useTableView ? 'Table View' : 'Classic View'"
            color="primary"
          />
        </div>
      <!-- Toggle Cal View -->
        <div v-if="useTableView ">
          <v-switch
            v-model="calView"
            class="pl-8"
            hide-details
            density="compact"
            :label="calView ? 'kcal' : 'kJ'"
            color="primary"
          />
        </div>
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
const useTableView = ref(false);
const calView = ref(false);

const nutrients = computed(() => {
  const nutrition = modelValue.value || {} as Nutrition;
  return [
    { label: "Energy", value: nutrition.calories, unit: "", special: true },
    { label: "Protein", value: nutrition.proteinContent, unit: "g" },
    { label: "Fat, total", value: nutrition.fatContent, unit: "g" },
    { label: "– Saturated", value: nutrition.saturatedFatContent, unit: "g", indent: true },
    { label: "Carbohydrate", value: nutrition.carbohydrateContent, unit: "g" },
    { label: "– Sugars", value: nutrition.sugarContent, unit: "g", indent: true },
    { label: "Dietary Fibre", value: nutrition.fiberContent, unit: "g" },
    { label: "Sodium", value: nutrition.sodiumContent, unit: "mg" },
  ];
});
</script>

<style lang="scss" scoped></style>
