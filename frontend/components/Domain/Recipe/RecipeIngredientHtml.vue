<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div v-html="safeMarkup"></div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { sanitizeIngredientHTML } from "~/composables/recipes/use-recipe-ingredients";
export default defineComponent({
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
    }
  }
});
</script>
