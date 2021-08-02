<template>
  <v-container>
    <RecipeCardSection :recipes="recipes"></RecipeCardSection>
  </v-container>
</template>
  
  <script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useApi } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/admin";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useApi();

    const recipes = ref<Recipe[] | null>([]);
    onMounted(async () => {
      const { data } = await api.recipes.getAll();
      recipes.value = data;
    });

    return { api, recipes };
  },
});
</script>
  