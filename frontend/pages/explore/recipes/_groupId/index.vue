<template>
  <v-container>
    <RecipeCardSection :icon="$globals.icons.primary" :title="$tc('page.all-recipes')" :recipes="recipes || []" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync, useRoute, useRouter } from "@nuxtjs/composition-api";
import { usePublicApi } from "~/composables/api/api-client";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";

export default defineComponent({
  components: { RecipeCardSection },
  layout: "basic",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const groupId = route.value.params.groupId;
    const api = usePublicApi();

    const recipes = useAsync(async () => {
      const { data, error } = await api.explore.allRecipes(groupId);

      if (error || !data) {
        console.error("error loading recipes -> ", error);
        router.push("/");
        return;
      }

      return data.items;
    });

    return {
      recipes,
    };
  },
});
</script>

<style scoped></style>
