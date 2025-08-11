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
          <div class="d-flex"></div> <!-- 3. Update Template: Add <v-select> for units-->
            <v-text-field
              density="compact"
             :model-value="modelValue[key]?.replace(/[a-zA-Z]+$/, '')"
             :label="labels[key].label"
             type="number"
             autocomplete="off"
             variant="underlined"
             class="flex-grow-1"
             @update:model-value="updateValue(key, $event)"
            />
            <v-select
              :items="unitOptions"
              v-model="selectedUnits[key]"
              class="ml-2"
              hide-details
              density="compact"
              style="max-width: 80px"
            />
          </div>
      </v-card-text>
      <v-list
        v-if="showViewer"
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
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes";
import type { Nutrition } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
import { defineComponent, ref, computed } from "vue";

interface Props {
  edit?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
});

const modelValue = defineModel<Nutrition>({ required: true });

const { labels } = useNutritionLabels();

    // 1. Add unit options and a selectedUnits object
    // In <script lang="ts">, inside setup
    
    // Defines an array called unitOptions that holds the list of available measurement units
    //This list is used to populate the <v-select> dropdown
    const unitOptions = ['g', 'mg', 'kcal', 'IU', 'µg']; // Extend as needed
    // Creates a reactive object selectedUnits using Vue’s ref()
    const selectedUnits = ref<Record<string, string>>({});

    // Initialize selected units from label suffix or default
    // Loops through all keys in the modelValue object passed as a prop
    Object.keys(props.modelValue).forEach((key) => {
      // This initializes the unit dropdown for each item with either the recommended label unit
      selectedUnits.value[key] = labels[key]?.suffix || 'g'; //// default unit
    });

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

    //function updateValue(key: number | string, event: Event) {
      //context.emit("update:modelValue", { ...props.modelValue, [key]: event });
    //}

    
    // 2. Update updateValue() to emit both value and selected unit
    // Replace the function
    function updateValue(key: string, value: string) {
      const updated = {
        ...props.modelValue,
        [key]: value + selectedUnits.value[key], // Append unit to the value
      };
      context.emit("update:modelValue", updated);
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
    // Build a new list that only contains nutritional information that has a value
    const renderedList = computed(() => {
      return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
        if (props.modelValue[key]?.trim()) {
          item[key] = {
            ...label,
            value: props.modelValue[key],
          };
        }
        return item;
      }, {});
    });

    return {
      labels,
      valueNotNull,
      showViewer,
      updateValue,
      renderedList,
      unitOptions, // 4. Return added items in setup()
      selectedUnits, // 4. Return added items in setup()
    };
  },
});
</script>

<style lang="scss" scoped></style>
