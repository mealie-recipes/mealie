<template>
  <div>
    <client-only>
      <RecipePage v-if="recipe" :recipe="recipe" />
    </client-only>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, useAsync, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicApi } from "~/composables/api/api-client";
import { useRecipeMeta } from "~/composables/recipes";

export default defineComponent({
  components: { RecipePage },
  layout: "basic",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const groupId = route.value.params.groupId;
    const slug = route.value.params.slug;
    const api = usePublicApi();

    const { meta, title } = useMeta();
    const { recipeMeta } = useRecipeMeta();

    const recipe = useAsync(async () => {
      const { data, error } = await api.explore.recipe(groupId, slug);

      if (error) {
        console.error("error loading recipe -> ", error);
        router.push("/");
      }

      if (data) {
        title.value = data?.name || "";
        const metaObj = recipeMeta(ref(data));
        meta.value = metaObj.meta;
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
