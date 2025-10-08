<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1" />

      <!-- ================= Editor Mode ================= -->
      <v-card-text v-if="edit">
        <!-- Built-in nutrition rows -->
        <div
          v-for="(item, key, index) in labels"
          :key="index"
          class="d-flex"
        >
          <v-text-field
            density="compact"
            :model-value="String(modelValue[key] || '')"
            :label="labels[key].label"
            type="number"
            autocomplete="off"
            variant="underlined"
            class="flex-grow-1"
            @update:model-value="val => updateValue(key, val)"
          />
          <v-select
            :items="unitOptions"
            v-model="modelValue[key + 'Unit']"
            class="ml-2"
            hide-details
            density="compact"
            style="max-width: 80px"
          />
        </div>

        <v-divider class="my-3" />

        <!-- Add Custom Nutrition Row -->
        <div class="d-flex align-center mb-2">
          <v-text-field
            v-model="newCustomName"
            label="Nutrient Name"
            density="compact"
            class="mr-2"
            style="max-width: 150px"
          />
          <v-text-field
            v-model="newCustomValue"
            label="Value"
            type="number"
            density="compact"
            class="mr-2"
            style="max-width: 100px"
          />
          <v-select
            v-model="newCustomUnit"
            :items="unitOptions"
            density="compact"
            hide-details
            style="max-width: 80px"
          />
          <v-btn
            size="small"
            class="ml-2"
            @click="addCustomNutrition"
          >
            Add
          </v-btn>
        </div>

        <!-- Existing Custom Nutrients -->
        <div
          v-for="(nutrient, name) in modelValue.customNutrition ?? {}"
          :key="name"
          class="d-flex align-center mb-1"
        >
          <v-text-field
            v-model="modelValue.customNutrition![name].value"
            :label="String(name)"
            type="number"
            density="compact"
            class="mr-2 flex-grow-1"
          />
          <v-select
            v-model="modelValue.customNutrition![name].unit"
            :items="unitOptions"
            density="compact"
            hide-details
            style="max-width: 80px"
            class="mr-2"
          />
          <v-btn
            size="small"
            color="error"
            @click="removeCustomNutrition(name)"
          >
            Remove
          </v-btn>
        </div>
      </v-card-text>

      <!-- ================= Viewer Mode ================= -->
      <v-list v-if="showViewer" density="compact" class="mt-0 pt-0">
        <!-- Built-in nutrients -->
        <v-list-item
          v-for="(item, key, index) in renderedList"
          :key="index"
          style="min-height: 25px"
        >
          <v-list-item-title class="pl-2 d-flex">
            <div>{{ item.label }}</div>
            <div class="ml-auto mr-1">{{ item.value }}</div>
            <div>{{ item.suffix }}</div>
          </v-list-item-title>
        </v-list-item>

        <!-- Custom nutrients -->
        <v-list-item
          v-for="(nutrient, name) in modelValue.customNutrition ?? {}"
          :key="name"
          style="min-height: 25px"
        >
          <v-list-item-title class="pl-2 d-flex">
            <div>{{ name }}</div>
            <div class="ml-auto mr-1">{{ nutrient.value }}</div>
            <div>{{ nutrient.unit }}</div>
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes/use-recipe-nutrition";
import type { Nutrition } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
import { ref, computed, onMounted } from "vue";
import { useUserApi } from "~/composables/api/api-client";

interface Props {
  edit?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
});

// v-model from parent
const modelValue = defineModel<Nutrition>({ required: true });
const { labels } = useNutritionLabels();

// Units state
const unitOptions = ref<string[]>([]);
onMounted(async () => {
  try {
    const api = useUserApi();
    const res = await api.nutrition.getUnits();
    unitOptions.value = res.units || ["g", "mg", "kcal", "IU", "µg"];
  } catch (err) {
    console.error("Failed to load nutrition units", err);
    unitOptions.value = ["g", "mg", "kcal", "IU", "µg"];
  }
});

// New custom nutrient inputs
const newCustomName = ref("");
const newCustomValue = ref("");
const newCustomUnit = ref("g");

// Methods
function updateValue(key: string, value: string) {
  const updated = { ...modelValue.value, [key]: value };
  modelValue.value = updated;
}

function addCustomNutrition() {
  if (!newCustomName.value.trim()) return;
  if (!modelValue.value.customNutrition) {
    modelValue.value.customNutrition = {};
  }
  modelValue.value.customNutrition[newCustomName.value] = {
    value: newCustomValue.value || "",
    unit: newCustomUnit.value || "",
  };
  newCustomName.value = "";
  newCustomValue.value = "";
  newCustomUnit.value = "g";
}

function removeCustomNutrition(name: string) {
  if (modelValue.value.customNutrition) {
    delete modelValue.value.customNutrition[name];
  }
}

// Computed
const valueNotNull = computed(() => {
  let key: keyof Nutrition;
  for (key in modelValue.value) {
    if (
      modelValue.value[key] !== null &&
      modelValue.value[key] !== "" &&
      key !== "customNutrition"
    ) {
      return true;
    }
  }
  return (
    modelValue.value.customNutrition &&
    Object.keys(modelValue.value.customNutrition).length > 0
  );
});

const showViewer = computed(() => !props.edit && valueNotNull.value);

const renderedList = computed(() => {
  return Object.entries(labels).reduce(
    (item: NutritionLabelType, [key, label]) => {
      const value = modelValue.value[key as keyof Nutrition];
      const unit = modelValue.value[key + "Unit" as keyof Nutrition];
      if (value && value.toString().trim()) {
        item[key] = {
          ...label,
          value: String(value),
          suffix: String(unit || ""),
        };
      }
      return item;
    },
    {}
  );
});
</script>

<style lang="scss" scoped></style>
