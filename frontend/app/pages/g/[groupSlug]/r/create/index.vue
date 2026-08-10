<template>
  <div />
</template>

<script setup lang="ts">
const route = useRoute();
const router = useRouter();
const auth = useMealieAuth();

onMounted(() => {
  // Force redirect to first valid page
  const groupSlug = route.params.groupSlug as string || auth.user.value?.groupSlug || "";
  router.replace(`/g/${groupSlug}/r/create/url`);
});
</script>
