<template>
  <div v-if="header" class="d-flex pt-2 align-center">
    <slot name="dragHandle" />
    <slot v-if="!$vuetify.display.mdAndDown" name="form" />
    <slot name="contextMenu" />
  </div>
  <slot v-else-if="!$vuetify.display.mdAndDown" name="form" />
  <slot v-if="$vuetify.display.mdAndDown" name="form" />
</template>

<script setup lang="ts">
defineProps<{ header: boolean }>();
</script>
