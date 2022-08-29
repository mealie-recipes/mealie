<template>
  <div>
    <RecipePage v-if="recipe" :recipe="recipe" />
  </div>
</template>

<script lang="ts">
import { defineComponent, useRoute } from "@nuxtjs/composition-api";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { useRecipe } from "~/composables/recipes";

export default defineComponent({
  components: { RecipePage },
  setup() {
    const route = useRoute();
    const slug = route.value.params.slug;

    const { recipe, loading } = useRecipe(slug);

    return {
      recipe,
      loading,
    };
  },
});
</script>
