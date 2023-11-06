<template>
  <div>
    <RecipeExplorerPage />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
});
</script>
