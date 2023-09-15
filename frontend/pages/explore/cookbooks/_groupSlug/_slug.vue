<template>
  <client-only>
    <CookbookPage :group-slug="groupSlug" />
  </client-only>
</template>

  <script lang="ts">
  import { defineComponent, useRoute } from "@nuxtjs/composition-api";
  import CookbookPage from "@/components/Domain/Cookbook/CookbookPage.vue";

  export default defineComponent({
    components: { CookbookPage },
    layout: "explore",
    setup() {
      const route = useRoute();
      const groupSlug = route.value.params.groupSlug;

      return {
        groupSlug,
      }
    },
  })
  </script>
