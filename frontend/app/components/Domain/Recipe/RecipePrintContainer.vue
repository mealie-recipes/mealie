<template>
  <div class="print-container">
    <RecipePrintView
      :recipe="recipe"
      :scale="scale"
      :density="'compact'"
    />
  </div>
</template>

<script setup lang="ts">
import RecipePrintView from "~/components/Domain/Recipe/RecipePrintView.vue";
import type { Recipe } from "~/lib/api/types/recipe";

interface Props {
  recipe: Recipe;
  scale?: number;
}

withDefaults(defineProps<Props>(), {
  scale: 1,
});
</script>

<style>
@media print {
  body,
  html {
    margin-top: 0 !important;
  }

  .print-container {
    display: block !important;
  }

  .v-main {
    display: block;
    padding: 0 !important;
    margin: 0 !important;
  }

  .v-main__wrap {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>

<style scoped>
.print-container {
  display: none;
}
</style>
