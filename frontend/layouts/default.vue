
<template>
  <DefaultLayout />
</template>

<script lang="ts">
import { defineComponent, ref, useRoute, useRouter } from "@nuxtjs/composition-api";
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";

export default defineComponent({
  components: { DefaultLayout },
  setup() {
    const route = useRoute();
    const router = useRouter();

    const groupSlug = ref<string | null>(route.value.params.groupSlug);
    const redirectPath = '/login';
    if (!groupSlug.value && route.value.fullPath !== redirectPath) {
      // the URL is invalid, so redirect to the login screen
      router.push({ path: redirectPath, replace: true });
    }
  }
});
</script>
