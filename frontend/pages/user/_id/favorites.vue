<template>
  <v-container>
    <RecipeCardSection
      v-if="recipes && isOwnGroup"
      :icon="$globals.icons.heart"
      :title="$tc('user.user-favorites')"
      :recipes="recipes"
      :query="query"
      @sortRecipes="assignSorted"
      @replaceRecipes="replaceRecipes"
      @appendRecipes="appendRecipes"
      @delete="removeRecipe"
    />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useRoute } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLazyRecipes } from "~/composables/recipes";
import { useLoggedInState } from "~/composables/use-logged-in-state";

export default defineComponent({
  components: { RecipeCardSection },
  middleware: "auth",
  setup() {
    const route = useRoute();
    const { isOwnGroup } = useLoggedInState();

    const userId = route.value.params.id;
    const query = { queryFilter: `favoritedBy.id = "${userId}"` }
    const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes();

    return {
      query,
      recipes,
      isOwnGroup,
      appendRecipes,
      assignSorted,
      removeRecipe,
      replaceRecipes,
    };
  },
  head() {
    return {
      title: this.$t("general.favorites") as string,
    };
  },
});
</script>

<style scoped></style>
