<template>
  <div />
</template>

<script lang="ts">
export default defineNuxtComponent({
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
