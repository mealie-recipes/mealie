<template>
  <div v-if="value && value.length > 0">
    <div
      v-if="!isCookMode"
      class="ingredients-header"
    >
      <h2 class="ingredients-header__title">
        {{ $t("recipe.ingredients") }}
      </h2>
      <div class="ingredients-header__actions">
        <slot name="header-append" />
        <AppButtonCopy
          :copy-text="ingredientCopyText"
        />
      </div>
    </div>
    <div class="ingredients-list">
      <div
        v-for="(ingredient, index) in value"
        :key="'ingredient' + index"
      >
        <h3
          v-if="showTitleEditor[index]"
          class="ingredients-list__section"
        >
          {{ ingredient.title }}
        </h3>
        <div
          class="ingredient-row ingredient-list-item"
          :class="{ 'ingredient-row--checked': isChecked(index) }"
          @click="toggleChecked(index)"
        >
          <button
            type="button"
            role="checkbox"
            class="ingredient-row__check"
            :aria-checked="isChecked(index)"
            :aria-label="parseIngredientText(ingredient, scale, false)"
            @click.stop="toggleChecked(index)"
          >
            <svg v-if="isChecked(index)" width="11" height="9" viewBox="0 0 12 10" aria-hidden="true"><polyline
              points="1.5,5 4.5,8 10.5,1.8"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            /></svg>
          </button>
          <RecipeIngredientListItem
            class="ingredient-row__text"
            :ingredient="ingredient"
            :scale="scale"
            show-substitutions
          />
        </div>
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
.ingredients-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.ingredients-header__title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--mealie-ink);
}

.ingredients-header__actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ingredients-list {
  margin-top: 8px;
}

.ingredients-list__section {
  margin-top: 18px;
  padding-bottom: 6px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
  border-bottom: 1px solid var(--mealie-hairline);
}

.ingredient-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-height: 40px;
  padding: 8px 0;
  border-bottom: 1px solid var(--mealie-hairline);
  box-sizing: border-box;
  cursor: pointer;
}

.ingredient-row__check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
  padding: 0;
  border: 0;
  border-radius: 10px;
  background: transparent;
  box-shadow: inset 0 0 0 1.6px var(--mealie-checkbox-ring);
  color: rgb(var(--v-theme-on-primary));
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    box-shadow 0.15s ease;
}

.ingredient-row__check:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.ingredient-row--checked .ingredient-row__check {
  background: rgb(var(--v-theme-primary));
  box-shadow: none;
}

.ingredient-row__text {
  flex: 1;
  min-width: 0;
  font-size: 15px !important;
  color: var(--mealie-ink);
  transition: color 0.15s ease;
}

.ingredient-row--checked .ingredient-row__text {
  color: var(--mealie-text-quaternary);
  text-decoration: line-through;
}

.dense-markdown p {
  margin: auto !important;
}
</style>
