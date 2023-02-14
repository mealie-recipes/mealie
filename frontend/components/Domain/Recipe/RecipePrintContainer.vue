<template>
<div class="print-container">
  <RecipePrintView :recipe="recipe" :scale="scale" dense />
</div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipePrintView from "~/components/Domain/Recipe/RecipePrintView.vue";
import { Recipe } from "~/lib/api/types/recipe";

export default defineComponent({
  components: {
    RecipePrintView,
  },
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },
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
