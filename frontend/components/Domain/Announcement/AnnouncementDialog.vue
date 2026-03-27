<template>
  <BaseDialog
    v-model="dialog"
  >
    test <!-- TODO -->
  </BaseDialog>
</template>

<script setup lang="ts">
const dialog = defineModel<boolean>({ default: false });
</script>
