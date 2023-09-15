<template>
  <div v-if="groupSlug">
    <client-only>
      <RecipeExplorerPage :group-slug="groupSlug" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { defineComponent, useRoute, useRouter } from "@nuxtjs/composition-api";
import { invoke } from "@vueuse/core";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";
import { usePublicExploreApi } from "~/composables/api/api-client";

export default defineComponent({
  components: { RecipeExplorerPage },
  layout: "explore",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const groupSlug = route.value.params.groupSlug;
    const api = usePublicExploreApi(groupSlug);

    invoke(async () => {
      if (!groupSlug) {
        return;
      }

      // try to fetch one tag to make sure the group slug is valid
      const { data } = await api.explore.tags.getAll(1, 1);
      if (!data) {
        // the group slug is invalid, so leave the page (this results in a 404)
        router.push("/explore/recipes");
      }
    });

    return {
      groupSlug,
    };
  },
});
</script>
