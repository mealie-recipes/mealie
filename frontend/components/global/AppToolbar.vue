<template>
  <v-toolbar flat>
    <BaseButton color="null" rounded secondary @click="$router.go(-1)">
      <template #icon> {{ $globals.icons.arrowLeftBold }}</template>
      Back
    </BaseButton>
    <slot></slot>
  </v-toolbar>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    back: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style lang="scss" scoped>
</style>