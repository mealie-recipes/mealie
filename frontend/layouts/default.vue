
<template>
  <DefaultLayout />
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRoute, useRouter } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";

export default defineComponent({
  components: { DefaultLayout },
  setup() {
    const { $auth } = useContext();
    const loggedIn = computed(() => $auth.loggedIn);
    const route = useRoute();
    const router = useRouter();

    const api = useUserApi();
    async function insertGroupSlugIntoRoute() {
      if (route.value.params['groupSlug']) {
        return;
      }

      const { data: group } = await api.groups.getCurrentUserGroup();
      if (!group) {
        return;
      }

      let routeVal = route.value.fullPath || "/";
      if (routeVal[0] !== "/") {
        routeVal = `/${routeVal}`;
      }

      const routeComponents = route.value.fullPath.split("/");
      if (routeComponents.length < 2 || routeComponents[1].toLowerCase() !== group.slug.toLowerCase()) {
        await router.push(`/${group.slug}${routeVal}`);
      }
    }

    if (loggedIn.value) {
      insertGroupSlugIntoRoute();
    }
  }
});
</script>
