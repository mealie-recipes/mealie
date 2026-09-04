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
    transition: all 0.3s cubic-bezier(0.5, -0.23, 0.5, 1.25);
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
    transform: scale(0.01) rotate(10deg);
    transform-origin: center;
  }
}
</style>
