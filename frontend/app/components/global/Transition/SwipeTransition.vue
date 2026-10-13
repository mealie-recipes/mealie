<template>
  <TransitionGroup v-if="group" :name="`swipe-${direction}`" appear class="overflow-x-hidden-child">
    <slot />
  </TransitionGroup>
  <Transition v-else :name="`swipe-${direction}`" mode="out-in" appear class="overflow-x-hidden-child">
    <slot />
  </Transition>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  direction: "left" | "right";
  group?: boolean;
}>(), {
  group: false,
});
</script>

<style lang="scss">
.swipe-left {
  &-move,
  &-enter-active,
  &-leave-active {
    transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
  }
  &-enter-from {
    transform: translateX(30px);
  }
  &-leave-to {
    transform: translateX(-30px);
  }
}
.swipe-right {
  &-move,
  &-enter-active,
  &-leave-active {
    transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  }

  &-enter-from,
  &-leave-to {
    opacity: 0;
  }
  &-enter-from {
    transform: translateX(-30px);
  }
  &-leave-to {
    transform: translateX(30px);
  }
}
*:has(.overflow-x-hidden-child) {
  overflow-x: hidden;
}
</style>
