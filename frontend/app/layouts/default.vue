<template>
  <DefaultLayout />
</template>

<script setup lang="ts">
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";
import { useGlobalI18n } from "~/composables/use-global-i18n";

useGlobalI18n(); // ensure i18n is initialized
</script>
