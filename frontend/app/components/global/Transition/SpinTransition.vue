<template>
  <TransitionGroup name="spin" appear>
    <slot />
  </TransitionGroup>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
defineProps<{}>();
</script>

<style lang="scss">
.spin {
  &-move,
  &-enter-active,
  &-leave-active {
    transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
    transform: scale(0.9);
    transform-origin: center;
  }
}
</style>
