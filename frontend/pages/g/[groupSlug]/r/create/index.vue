<template>
  <div />
</template>

<script setup lang="ts">
const router = useRouter();
onMounted(() => {
  // Force redirect to first valid page
  router.replace("/r/create/url");
});
</script>
