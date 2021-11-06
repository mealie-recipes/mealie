<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('general.recent')"
      :recipes="recentRecipes"
    ></RecipeCardSection>
  </v-container>
</template>
  
  <script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useRecipes, recentRecipes } from "~/composables/recipes";
import { useStaticRoutes } from "~/composables/api";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const { assignSorted } = useRecipes(false);
    useStaticRoutes();
    return { recentRecipes, assignSorted };
  },
});
</script>
  