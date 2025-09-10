<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div v-html="safeMarkup" />
</template>

<script setup lang="ts">
import { sanitizeIngredientHTML } from "~/composables/recipes/use-recipe-ingredients";

interface Props {
  markup: string;
}
const props = defineProps<Props>();

const safeMarkup = computed(() => sanitizeIngredientHTML(props.markup));
</script>
