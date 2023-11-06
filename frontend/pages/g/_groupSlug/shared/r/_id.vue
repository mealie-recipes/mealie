<template>
  <div>
    <client-only>
      <RecipePage v-if="recipe" :recipe="recipe" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useAsync, useContext, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicApi } from "~/composables/api/api-client";

export default defineComponent({
  components: { RecipePage },
  layout: "basic",
  setup() {
    const { $auth } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const router = useRouter();
    const recipeId = route.value.params.id;
    const api = usePublicApi();

    const { title } = useMeta();

    const recipe = useAsync(async () => {
      const { data, error } = await api.shared.getShared(recipeId);

      if (error) {
        console.error("error loading recipe -> ", error);
        router.push(`/g/${groupSlug.value}`);
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
