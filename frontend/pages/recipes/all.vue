<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="recipes"
      :use-pagination="true"
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
import { Recipe } from "~/types/api-types/recipe";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const { recipes, fetchMore } = useLazyRecipes();

    function appendRecipes(val: Array<Recipe>) {
      val.forEach((recipe) => {
        recipes.value.push(recipe);
      });
    }

    function assignSorted(val: Array<Recipe>) {
      recipes.value = val;
    }

    function removeRecipe(slug: string) {
      for (let i = 0; i < recipes?.value?.length; i++) {
        if (recipes?.value[i].slug === slug) {
          recipes?.value.splice(i, 1);
          break;
        }
      }
    }

    function replaceRecipes(val: Array<Recipe>) {
      recipes.value = val;
    }

    return { appendRecipes, assignSorted, recipes, removeRecipe, replaceRecipes };
  },
  head() {
    return {
      title: this.$t("page.all-recipes") as string,
    };
  },
});
</script>
