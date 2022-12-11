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
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useRecipes, recentRecipes } from "~/composables/recipes";
import { useStaticRoutes } from "~/composables/api";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  components: { RecipeCardSection },
  async setup() {
    const { assignSorted } = useRecipes(false);
    const { $auth } = useContext();

    useStaticRoutes();

    const api = useUserApi();
    if ($auth.user.iss) {
      // this is oidc, get the user from the server and set it
      const { data } = await api.users.getSelf();

      console.log(data);

      $auth.setUser(data);
    }

    return { recentRecipes, assignSorted };
  },
});
</script>
