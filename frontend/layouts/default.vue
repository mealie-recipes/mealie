
<template>
  <DefaultLayout />
</template>

<script lang="ts">
import { defineComponent, useRoute, useRouter } from "@nuxtjs/composition-api";
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";
import { useGroupSlugRoute } from "~/composables/use-group-slug-route";

export default defineComponent({
  components: { DefaultLayout },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const { getGroupSlug } = useGroupSlugRoute();

    async function verifyGroupSlugParam() {
      const groupSlugParam = route.value.params.groupSlug;
      const groupSlug = await getGroupSlug();

      if (groupSlug && groupSlugParam !== groupSlug) {
        const index = route.value.fullPath.indexOf(groupSlugParam) + groupSlugParam.length;
        const newPath = `/${groupSlug}${route.value.fullPath.slice(index)}`
        await router.push({ path: newPath, replace: true });
      }
    }

    const redirectPath = "/login";
    if (!route.value.params.groupSlug && route.value.fullPath !== redirectPath) {
      // the URL is invalid, so redirect to the login screen
      router.push({ path: redirectPath, replace: true });
    } else {
      verifyGroupSlugParam();
    }
  }
});
</script>
