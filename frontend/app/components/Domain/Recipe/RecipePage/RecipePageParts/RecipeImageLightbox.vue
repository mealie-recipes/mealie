<template>
  <v-dialog
    v-model="model"
    fullscreen
    scrim="black"
    transition="fade-transition"
  >
    <div
      class="lightbox-content"
      :style="{ backgroundColor: scrimColor }"
      @click="model = false"
    >
      <v-img
        v-if="imageUrl"
        :src="imageUrl"
        contain
        max-height="100vh"
        max-width="100vw"
        class="lightbox-img"
        :style="{ boxShadow: imageShadow }"
      />
    </div>
  </v-dialog>
</template>

<script setup lang="ts">
import { useTheme } from "vuetify";

interface Props {
  imageUrl?: string;
}

defineProps<Props>();
const model = defineModel<boolean>({ required: true });

const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);

const scrimColor = computed(() =>
  isDark.value ? "rgba(0, 0, 0, 0.75)" : "rgba(255, 255, 255, 0.75)",
);

const imageShadow = computed(() =>
  isDark.value ? "0 0 60px rgba(255, 255, 255, 0.15)" : "0 8px 40px rgba(0, 0, 0, 0.4)",
);
</script>

<style scoped>
.lightbox-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  cursor: zoom-out;
  transition: background-color 0.2s ease;
}

.lightbox-img {
  cursor: zoom-out;
  transition: box-shadow 0.2s ease;
}
</style>
