<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0 d-flex align-start">
        <div>{{ $t("recipe.nutrition") }}</div>
        <v-spacer />
        <v-btn
          v-if="mealplan"
          icon
          size="small"
          class="ml-2 mb-1"
          @click="emit('close-nutrition')"
        >
          <v-icon
            class="handle"
            :size="24"
            style="cursor: move;margin: auto;"
          >
            {{ $globals.icons.close }}
          </v-icon>
        </v-btn>
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
      <div v-if="showViewer">
        <v-list
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
  mealplan?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
  mealplan: false,
});

const modelValue = defineModel<Nutrition>({ required: true });

const emit = defineEmits<{ "close-nutrition": () => void }>();

const { labels } = useNutritionLabels();
const valueNotNull = computed(() => {
  let key: keyof Nutrition;
  for (key in modelValue.value) {
    const val = modelValue.value[key];
    if (val !== null && val !== undefined) {
      if (typeof val === "string") {
        if (val.trim() !== "") {
          return true;
        }
      }
      else {
        return true;
      }
    }
  }
  return false;
});

const showViewer = computed(() => !props.edit && valueNotNull.value);

function updateValue(key: number | string, newVal: string | number | null) {
  // Normalize stored value:
  // - empty string / null / undefined => null
  // - numeric values stay numbers
  // - strings are trimmed; if they represent a pure number, store as number
  let stored: string | number | null = null;

  if (newVal === null || newVal === undefined || newVal === "") {
    stored = null;
  }
  else if (typeof newVal === "number") {
    stored = newVal;
  }
  else {
    const t = (newVal as string).trim();
    if (t === "") {
      stored = null;
    }
    else {
      const parsed = Number(t);
      stored = !Number.isNaN(parsed) && String(parsed) === t ? parsed : t;
    }
  }

  modelValue.value = { ...modelValue.value, [String(key)]: stored as any };
}

// Build a new list that only contains nutritional information that has a value
const renderedList = computed(() => {
  return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
    const val = modelValue.value[key as keyof Nutrition];
    if (val !== null && val !== undefined) {
      if (typeof val === "string") {
        const t = val.trim();
        if (t === "") {
          return item;
        }
        const parsed = Number(t);
        item[key] = {
          ...label,
          value: !Number.isNaN(parsed) && String(parsed) === t ? parsed : t,
        };
      }
      else if (typeof val === "number") {
        item[key] = {
          ...label,
          value: val,
        };
      }
    }
    return item;
  }, {});
});
</script>

<style lang="scss" scoped></style>
