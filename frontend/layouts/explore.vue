
<template>
    <DefaultLayout />
  </template>

<script lang="ts">
import { computed, defineComponent, useContext, useRoute } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";

export default defineComponent({
  components: { DefaultLayout },
  setup() {
  const { $auth } = useContext();
  const loggedIn = computed(() => $auth.loggedIn);
  const route = useRoute();

  async function insertGroupSlugIntoRoute() {
    const api = useUserApi();
    const { data: group } = await api.groups.getCurrentUserGroup();
    if (!group) {
      return;
    }

    console.log(route.value.fullPath.split("/"));
  }

  if (loggedIn.value) {
    insertGroupSlugIntoRoute();
  }
}
});
</script>
