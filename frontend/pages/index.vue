<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('general.recent')"
      :recipes="recipes"
    ></RecipeCardSection>
  </v-container>
</template>
  
  <script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/admin";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useApiSingleton();

    const recipes = ref<Recipe[] | null>([]);
    onMounted(async () => {
      const { data } = await api.recipes.getAll();
      recipes.value = data;
    });

    return { api, recipes };
  },
});
</script>
  