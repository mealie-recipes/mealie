<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1" />
      <div v-if="loading">
        <AppLoader
          v-if="loading"
          :loading="loading"
          waiting-text=""
        />
      </div>
      <div v-else>
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
                {{ typeof item.value === 'string' ? Math.round(Number(item.value)) : 0 }}
              </div>
              <div>{{ item.suffix }}</div>
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
      <div class="d-flex justify-end pa-2">
        <BaseButton
          v-if="appInfo && appInfo.enableOpenai && edit"
          :icon="$globals.icons.refresh"
          :disabled="loading"
          @click="emit('fetch-nutrition-info')"
        >
          Fetch Nutrition Data
        </BaseButton>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes";
import type { Nutrition } from "~/lib/api/types/recipe";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
import { useAppInfo } from "~/composables/api/use-app-info";

interface Props {
  edit?: boolean;
  loading?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
});

const modelValue = defineModel<Nutrition>({ required: true });

const emit = defineEmits<{
  "fetch-nutrition-info": [];
}>();

const { labels } = useNutritionLabels();
const appInfo = useAppInfo();

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
</script>

<style lang="scss" scoped></style>
