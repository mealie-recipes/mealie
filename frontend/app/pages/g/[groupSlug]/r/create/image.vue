<template>
  <div />
</template>

<script setup lang="ts">
const route = useRoute();
const router = useRouter();
const auth = useMealieAuth();

// The image importer was folded into the AI importer, which takes images alongside other content.
// Kept as a redirect so existing links and bookmarks still land somewhere useful.
onMounted(() => {
  const groupSlug = route.params.groupSlug as string || auth.user.value?.groupSlug || "";
  router.replace(`/g/${groupSlug}/r/create/ai`);
});
</script>
