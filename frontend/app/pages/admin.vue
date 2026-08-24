<template>
  <NuxtPage />
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ["admin-only"],
});
</script>
