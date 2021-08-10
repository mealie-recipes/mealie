<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="allRecipes"
      @sort="assignSorted"
    ></RecipeCardSection>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useRecipes, allRecipes } from "~/composables/use-recipes";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const { assignSorted } = useRecipes(true);

    return { allRecipes, assignSorted };
  },
});
</script>
  