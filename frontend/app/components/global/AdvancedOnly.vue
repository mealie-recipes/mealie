<template>
  <slot v-if="advanced" />
</template>

<script setup lang="ts">
/**
 * Renderless component that only renders if the user is logged in.
 * and has advanced options toggled.
 */
const auth = useMealieAuth();

const advanced = auth.user.value?.advanced || false;
</script>
