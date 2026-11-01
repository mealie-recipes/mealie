<template>
  <div v-if="header" class="d-flex pt-2 align-center">
    <slot name="dragHandle" />
    <slot v-if="!stacked" name="form" />
    <slot name="contextMenu" />
  </div>
  <slot v-else-if="!stacked" name="form" />
  <slot v-if="stacked" name="form" />
</template>

<script setup lang="ts">
defineProps<{ header: boolean; stacked: boolean }>();
</script>
