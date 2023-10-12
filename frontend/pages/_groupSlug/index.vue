<template>
  <div v-if="groupSlug">
    <RecipeExplorerPage :group-slug="groupSlug" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { invoke } from "@vueuse/core";
import { useUserApi } from "~/composables/api/api-client";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
  setup() {
    const api = useUserApi();
    const groupSlug = ref<string>();

    invoke(async () => {
      const { data } = await api.users.getSelfGroup();
      groupSlug.value = data?.slug;
    });

    return {
      groupSlug,
    };
  },
});
</script>
