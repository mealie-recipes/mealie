<template>
  <div v-if="groupSlug">
    <RecipeExplorerPage :group-slug="groupSlug" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useRoute } from "@nuxtjs/composition-api";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
  setup() {
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug);

    return {
      groupSlug,
    };
  },
});
</script>
