<template>
  <div v-if="groupSlug">
    <RecipeExplorerPage :group-slug="groupSlug" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import { invoke } from "@vueuse/core";
import { useUserApi } from "~/composables/api/api-client";
import RecipeExplorerPage from "~/components/Domain/Recipe/RecipeExplorerPage.vue";

export default defineComponent({
  components: { RecipeExplorerPage },
  setup() {
    const { $auth } = useContext();
    const api = useUserApi();

    // @ts-ignore $auth.user is typed as unknown, even though it's a user
    const groupId: string | undefined = $auth.user?.groupId;
    const groupSlug = ref<string>();


    invoke(async () => {
      if (!groupId) {
        return;
      }

      const { data } = await api.groups.getOne(groupId);
      if (data) {
        groupSlug.value = data.slug;
      }
    });

    return {
      groupSlug,
    };
  },
});
</script>
