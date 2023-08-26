<template>
  <div v-if="groupSlug">
    <client-only>
      <RecipeExplorerPage :group-slug="groupSlug" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { defineComponent, useRoute } from "@nuxtjs/composition-api";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
  layout: "basic",
  setup() {
    const route = useRoute();
    const groupSlug = route.value.params.groupSlug;

    return {
      groupSlug,
    };
  },
});
</script>
