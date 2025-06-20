<script setup lang="ts">
definePageMeta({
  middleware: ["sidebase-auth", "admin-only"],
});
</script>

<template>
  <NuxtPage />
</template>
