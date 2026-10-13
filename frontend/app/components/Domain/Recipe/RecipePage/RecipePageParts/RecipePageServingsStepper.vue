<template>
  <div
    v-if="baseServings"
    class="servings-stepper"
    role="group"
    :aria-label="$t('recipe.servings')"
  >
    <button
      type="button"
      class="servings-stepper__btn"
      :disabled="!canScale || servings <= 1"
      :aria-label="$t('recipe-page.fewer-servings')"
      @click="step(-1)"
    >
      −
    </button>
    <button
      type="button"
      class="servings-stepper__label"
      :disabled="scale === 1"
      :title="scale === 1 ? undefined : $t('recipe.reset-servings-count')"
      @click="scale = 1"
    >
      {{ $t("recipe-page.servings-count", { count: displayServings }, servingsForPlural) }}
    </button>
    <button
      type="button"
      class="servings-stepper__btn"
      :disabled="!canScale"
      :aria-label="$t('recipe-page.more-servings')"
      @click="step(1)"
    >
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const props = defineProps<{ recipe: NoUndefinedField<Recipe> }>();

const scale = defineModel<number>({ default: 1 });

const baseServings = computed(() => props.recipe.recipeServings || props.recipe.recipeYieldQuantity || 0);

// scaling only means something once ingredients are parsed into amounts and units
const canScale = computed(() =>
  (props.recipe.recipeIngredient || []).some(ingredient => ingredient.food || ingredient.unit),
);

const servings = computed(() => Math.round(baseServings.value * scale.value * 100) / 100);
const displayServings = computed(() => String(servings.value));
const servingsForPlural = computed(() => Math.max(1, Math.round(servings.value)));

/** steps to the next whole serving, so a scaled 2.5 goes to 3 or 2 rather than 3.5 or 1.5 */
function step(direction: 1 | -1) {
  const current = servings.value;
  const next = direction > 0 ? Math.floor(current) + 1 : Math.ceil(current) - 1;
  scale.value = Math.max(1, next) / baseServings.value;
}
</script>

<style scoped>
.servings-stepper {
  display: inline-flex;
  align-items: center;
  height: 30px;
  border-radius: 15px;
  background: var(--mealie-fill);
  white-space: nowrap;
  flex-shrink: 0;
}

.servings-stepper__btn {
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 15px;
  background: transparent;
  color: rgb(var(--v-theme-primary));
  font: inherit;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
}

.servings-stepper__btn:disabled {
  color: var(--mealie-text-quaternary);
  cursor: default;
}

.servings-stepper__label {
  border: 0;
  background: transparent;
  padding: 0 2px;
  color: var(--mealie-ink);
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.servings-stepper__label:disabled {
  cursor: default;
}

.servings-stepper__btn:focus-visible,
.servings-stepper__label:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -2px;
}
</style>
