<template>
  <v-container>
    <RecipeCardSection v-if="user" :icon="$globals.icons.heart" title="User Favorites" :recipes="user.favoriteRecipes">
    </RecipeCardSection>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync, useRoute } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useUserApi();
    const route = useRoute();

    const userId = route.value.params.id;

    const user = useAsync(async () => {
      const { data } = await api.users.getFavorites(userId);
      return data;
    }, useAsyncKey());

    return {
      user,
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
