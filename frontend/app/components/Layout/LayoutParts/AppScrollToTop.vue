<template>
  <v-fade-transition>
    <v-btn
      v-if="showButton"
      icon
      position="fixed"
      location="bottom right"
      class="ma-4"
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
const showButton = ref(false);
const threshold = 400;

function onScroll() {
  showButton.value = document.documentElement.scrollTop > threshold;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => {
  window.addEventListener("scroll", onScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", onScroll);
});
</script>
