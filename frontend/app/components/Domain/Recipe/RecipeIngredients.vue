<template>
  <div v-if="value && value.length > 0">
    <div
      v-if="!isCookMode"
      class="d-flex justify-start"
    >
      <h2 class="mt-1 text-h5 font-weight-medium opacity-80">
        {{ $t("recipe.ingredients") }}
      </h2>
      <AppButtonCopy
        btn-class="ml-auto"
        :copy-text="ingredientCopyText"
      />
    </div>
    <div>
      <div
        v-for="(ingredient, index) in value"
        :key="'ingredient' + index"
      >
        <h3
          v-if="showTitleEditor[index]"
          class="mt-4 mb-0"
        >
          {{ ingredient.title }}
        </h3>
        <v-divider v-if="showTitleEditor[index]" class="my-2" />
        <v-list-item
          density="compact"
          class="px-0 py-1 ingredient-list-item"
          @click.stop="toggleChecked(index)"
        >
          <template #prepend>
            <v-checkbox
              :model-value="isChecked(index)"
              hide-details
              class="pt-0 my-auto py-auto"
              color="secondary"
              density="comfortable"
              @click.stop
              @update:model-value="setChecked(index, !!$event)"
            />
          </template>
          <v-list-item-title>
            <RecipeIngredientListItem
              :ingredient="ingredient"
              :scale="scale"
              show-substitutions
            />
          </v-list-item-title>
        </v-list-item>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
import { useSessionStorage } from "@vueuse/core";
import { useIngredientTextParser } from "~/composables/recipes";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

interface Props {
  value?: RecipeIngredient[];
  scale?: number;
  isCookMode?: boolean;
  storageKey?: string;
}
const props = withDefaults(defineProps<Props>(), {
  value: () => [],
  scale: 1,
  isCookMode: false,
  storageKey: undefined,
});

const { parseIngredientText } = useIngredientTextParser();

function validateTitle(title?: string | null) {
  return !(title === undefined || title === "" || title === null);
}

const transientChecked = ref<Record<string, boolean>>({});
const sessionChecked = props.storageKey
  ? useSessionStorage<Record<string, boolean>>(props.storageKey, {})
  : null;
const showTitleEditor = computed(() => props.value.map(x => validateTitle(x.title)));

const ingredientCopyText = computed(() => {
  const components: string[] = [];
  props.value.forEach((ingredient) => {
    if (ingredient.title) {
      if (components.length) {
        components.push("");
      }

      components.push(`[${ingredient.title}]`);
    }

    components.push(parseIngredientText(ingredient, props.scale, false));
  });

  return components.join("\n");
});

function toggleChecked(index: number) {
  setChecked(index, !isChecked(index));
}

function checkedState() {
  return sessionChecked?.value ?? transientChecked.value;
}

function checkedKey(index: number) {
  const referenceId = props.value[index]?.referenceId;
  return referenceId ? `ref:${referenceId}` : `idx:${index}`;
}

function isChecked(index: number) {
  return !!checkedState()[checkedKey(index)];
}

function setChecked(index: number, value: boolean) {
  const state = checkedState();
  state[checkedKey(index)] = value;

  if (sessionChecked) {
    sessionChecked.value = { ...state };
  }
  else {
    transientChecked.value = { ...state };
  }
}
</script>

<style>
.dense-markdown p {
  margin: auto !important;
}

/* vuetify clips both of these, which would swallow the substitution button's tap target
   where it reaches past the line of text */
.ingredient-list-item .v-list-item__content,
.ingredient-list-item .v-list-item-title {
  overflow: visible;
}
</style>
