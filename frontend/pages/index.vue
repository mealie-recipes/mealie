<template>
</template>

<script lang="ts">
import { defineComponent, useContext, useRouter } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import { useGroupSlugRoute } from "~/composables/use-group-slug-route";
export default defineComponent({
  layout: "basic",
  setup() {
    const { $auth } = useContext();
    const { groupSlug } = useGroupSlugRoute();
    const router = useRouter();

    if (!$auth.loggedIn) {
      router.push("/login");
    }

    whenever(
      () => groupSlug.value,
      () => router.push(`/${groupSlug.value}`)
    );
  }
});
</script>
