<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div v-html="safeMarkup" />
</template>

<script lang="ts">
import { sanitizeIngredientHTML } from "~/composables/recipes/use-recipe-ingredients";

export default defineNuxtComponent({
  props: {
    markup: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const safeMarkup = computed(() => sanitizeIngredientHTML(props.markup));
    return {
      safeMarkup,
    };
  },
});
</script>
