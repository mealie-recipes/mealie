<template>
  <v-container>
    <RecipeCardSection v-if="user && isOwnGroup" :icon="$globals.icons.heart" :title="$tc('user.user-favorites')" :recipes="user.favoriteRecipes">
    </RecipeCardSection>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync, useRoute } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  components: { RecipeCardSection },
  middleware: "auth",
  setup() {
    const api = useUserApi();
    const route = useRoute();
    const { isOwnGroup } = useLoggedInState();

    const userId = route.value.params.id;

    const user = useAsync(async () => {
      const { data } = await api.users.getFavorites(userId);
      return data;
    }, useAsyncKey());

    return {
      user,
      isOwnGroup,
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
