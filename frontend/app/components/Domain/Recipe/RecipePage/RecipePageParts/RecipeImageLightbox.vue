<template>
  <v-dialog
    v-model="model"
    fullscreen
    scrim="black"
    transition="fade-transition"
  >
    <div class="lightbox-content" @click="model = false">
      <v-img
        v-if="imageUrl"
        :src="imageUrl"
        contain
        max-height="100vh"
        max-width="100vw"
        class="lightbox-img"
      />
      <iframe
        v-else-if="pdfUrl"
        :src="pdfUrl"
        class="lightbox-pdf"
        frameborder="0"
        @click.stop
      />
    </div>
  </v-dialog>
</template>

<script setup lang="ts">
interface Props {
  imageUrl?: string;
  pdfUrl?: string;
}

defineProps<Props>();
const model = defineModel<boolean>({ required: true });
</script>

<style scoped>
.lightbox-content {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  cursor: zoom-out;
}

.lightbox-img {
  cursor: zoom-out;
}

.lightbox-pdf {
  width: 100vw;
  height: 100vh;
  cursor: default;
}
</style>
