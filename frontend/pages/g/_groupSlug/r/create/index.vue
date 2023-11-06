<template>
  <div></div>
</template>

<script lang="ts">
import { defineComponent, onMounted, useRouter } from "@nuxtjs/composition-api";

export default defineComponent({
  setup() {
    const router = useRouter();
    onMounted(() => {
      // Force redirect to first valid page
      router.replace("/r/create/url");
    });
    return {};
  },
});
</script>
