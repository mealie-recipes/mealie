<script setup lang="ts">
definePageMeta({
  middleware: ["admin-only"],
});
</script>

<template>
  <NuxtPage />
</template>
