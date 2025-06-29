<template>
  <v-container>
    <RecipeCardSection
      v-if="recipes && isOwnGroup"
      :icon="$globals.icons.heart"
      :title="$t('user.user-favorites')"
      :recipes="recipes"
      :query="query"
      @sort-recipes="assignSorted"
      @replace-recipes="replaceRecipes"
      @append-recipes="appendRecipes"
      @delete="removeRecipe"
    />
  </v-container>
</template>

<script lang="ts">
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLazyRecipes } from "~/composables/recipes";
import { useLoggedInState } from "~/composables/use-logged-in-state";

export default defineNuxtComponent({
  components: { RecipeCardSection },
  middleware: "sidebase-auth",
  setup() {
    const route = useRoute();
    const i18n = useI18n();
    const { isOwnGroup } = useLoggedInState();

    useSeoMeta({
      title: i18n.t("general.favorites"),
    });

    const userId = route.params.id;
    const query = { queryFilter: `favoritedBy.id = "${userId}"` };
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
});
</script>

<style scoped></style>
