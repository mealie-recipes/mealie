<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="recipes"
      @sortRecipes="assignSorted"
      @replaceRecipes="replaceRecipes"
      @appendRecipes="appendRecipes"
      @delete="removeRecipe"
    ></RecipeCardSection>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLazyRecipes } from "~/composables/recipes";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes();
    return { appendRecipes, assignSorted, recipes, removeRecipe, replaceRecipes };
  },
  head() {
    return {
      title: this.$t("page.all-recipes") as string,
    };
  },
});
</script>
