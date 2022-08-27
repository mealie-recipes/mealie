<template>
  <div>
    <RecipePage v-if="recipe" :recipe="recipe" />
  </div>
</template>

<script lang="ts">
import { defineComponent, useAsync, useRoute, useRouter } from "@nuxtjs/composition-api";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicApi } from "~/composables/api/api-client";

export default defineComponent({
  components: { RecipePage },
  layout: "basic",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const groupId = route.value.params.groupId;
    const slug = route.value.params.slug;
    const api = usePublicApi();

    const recipe = useAsync(async () => {
      const { data, error } = await api.explore.recipe(groupId, slug);

      if (error) {
        router.push("/");
      }

      return data;
    });

    return {
      recipe,
      groupId,
      api,
    };
  },
});
</script>
