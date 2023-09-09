<template>
  <div v-if="recipe">
    <client-only>
      <RecipePage :recipe="recipe" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { defineComponent, useAsync, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicExploreApi } from "~/composables/api/api-client";

export default defineComponent({
  components: { RecipePage },
  layout: "explore",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const groupSlug = route.value.params.groupSlug;
    const recipeSlug = route.value.params.recipeSlug;
    const api = usePublicExploreApi(groupSlug);

    const { title } = useMeta();

    const recipe = useAsync(async () => {
      const { data, error } = await api.explore.recipes.getOne(recipeSlug);

      if (error) {
        console.error("error loading recipe -> ", error);
        router.push("/");
      }

      if (data) {
        title.value = data?.name || "";
      }

      return data;
    });

    return {
      recipe,
    };
  },
  head: {},
});
</script>
