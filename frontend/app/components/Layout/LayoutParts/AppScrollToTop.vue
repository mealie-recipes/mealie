<template>
  <v-fade-transition>
    <v-btn
      v-if="showButton"
      icon
      position="fixed"
      location="bottom right"
      class="scroll-to-top"
      color="primary"
      elevation="4"
      style="z-index: 999;"
      @click="scrollToTop"
    >
      <v-icon>{{ $globals.icons.arrowUp }}</v-icon>
    </v-btn>
  </v-fade-transition>
</template>

<script setup lang="ts">
import { scrollBehavior } from "~/composables/use-utils";

const showButton = ref(false);
const threshold = 400;

function onScroll() {
  showButton.value = document.documentElement.scrollTop > threshold;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: scrollBehavior() });
}

onMounted(() => {
  window.addEventListener("scroll", onScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", onScroll);
});
</script>

<style scoped>
.scroll-to-top {
  margin: 16px;
  margin-right: calc(16px + env(safe-area-inset-right));
  margin-bottom: calc(16px + env(safe-area-inset-bottom));
}
</style>
