<template>
  <div class="ingredient-link-label links-disabled">
    <SafeMarkdown v-if="baseText" :source="baseText" />
    <SafeMarkdown
      v-if="ingredient?.note"
      class="d-inline"
      :source="` ${ingredient.note}`"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import { useParsedIngredientText } from "~/composables/recipes";

interface Props {
  ingredient?: RecipeIngredient;
  scale?: number;
}

const { ingredient, scale = 1 } = defineProps<Props>();

const baseText = computed(() => {
  if (!ingredient) return "";
  const parsed = useParsedIngredientText(ingredient, scale);
  return [parsed.quantity, parsed.unit, parsed.name].filter(Boolean).join(" ").trim();
});
</script>

<style scoped>
.ingredient-link-label {
  display: block;
  line-height: 1.25;
  word-break: break-word;
  font-size: 0.95rem;
}
.links-disabled :deep(a) {
  pointer-events: none;
  cursor: default;
  color: var(--v-theme-primary);
  text-decoration: none;
}
</style>
