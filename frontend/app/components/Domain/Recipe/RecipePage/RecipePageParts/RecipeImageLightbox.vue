<template>
  <v-dialog
    v-model="model"
    fullscreen
    scrim="transparent"
    transition="fade-transition"
  >
    <div
      class="lightbox-content"
      :style="{ backgroundColor: scrimColor }"
      @click="onBackgroundClick"
    >
      <div ref="frameRef" class="lightbox-frame">
        <img
          v-if="imageUrl"
          :src="imageUrl"
          class="lightbox-img"
          draggable="false"
          :style="imgStyle"
          @load="onImageLoad"
          @click="onImageClick"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        >
      </div>
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
  isDark.value
    ? "0 0 24px rgba(255, 255, 255, 0.45), 0 0 140px rgba(255, 255, 255, 0.45)"
    : "0 6px 16px rgba(0, 0, 0, 0.55), 0 18px 80px rgba(0, 0, 0, 0.7)",
);

const ZOOM_SCALE = 2;

const zoomed = ref(false);
const pan = reactive({ x: 0, y: 0 });
const dragging = ref(false);
const dragMoved = ref(false);
let dragStart = { x: 0, y: 0, panX: 0, panY: 0 };

function resetZoom() {
  zoomed.value = false;
  pan.x = 0;
  pan.y = 0;
}

watch(model, (open) => {
  if (!open) {
    resetZoom();
  }
});

function onBackgroundClick() {
  model.value = false;
}

function onImageClick(event: MouseEvent) {
  event.stopPropagation();
  if (dragMoved.value) {
    dragMoved.value = false;
    return;
  }
  if (zoomed.value) {
    resetZoom();
  }
  else {
    zoomed.value = true;
  }
}

function onPointerDown(event: PointerEvent) {
  event.stopPropagation();
  if (!zoomed.value) {
    return;
  }
  dragging.value = true;
  dragMoved.value = false;
  dragStart = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
  (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) {
    return;
  }
  const dx = event.clientX - dragStart.x;
  const dy = event.clientY - dragStart.y;
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
    dragMoved.value = true;
  }
  pan.x = dragStart.panX + dx;
  pan.y = dragStart.panY + dy;
}

function onPointerUp(event: PointerEvent) {
  event.stopPropagation();
  dragging.value = false;
}

// The <img> box must be sized to the actual rendered pixels of the image (not the
// frame's bounding box) so the box-shadow/glow hugs the photo's real edges rather
// than the invisible letterboxed area object-fit:contain would otherwise leave.
const frameRef = ref<HTMLElement | null>(null);
const frameSize = reactive({ w: 0, h: 0 });
const naturalSize = reactive({ w: 0, h: 0 });

function updateFrameSize() {
  if (frameRef.value) {
    frameSize.w = frameRef.value.clientWidth;
    frameSize.h = frameRef.value.clientHeight;
  }
}

function onImageLoad(event: Event) {
  const img = event.target as HTMLImageElement;
  naturalSize.w = img.naturalWidth;
  naturalSize.h = img.naturalHeight;
  updateFrameSize();
}

onMounted(() => {
  updateFrameSize();
  window.addEventListener("resize", updateFrameSize);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateFrameSize);
});

const renderedSize = computed(() => {
  if (!naturalSize.w || !naturalSize.h || !frameSize.w || !frameSize.h) {
    return null;
  }

  const scale = Math.min(frameSize.w / naturalSize.w, frameSize.h / naturalSize.h);
  return { width: naturalSize.w * scale, height: naturalSize.h * scale };
});

const imgStyle = computed(() => ({
  ...(renderedSize.value
    ? { width: `${renderedSize.value.width}px`, height: `${renderedSize.value.height}px` }
    : {}),
  boxShadow: imageShadow.value,
  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoomed.value ? ZOOM_SCALE : 1})`,
  transition: dragging.value ? "none" : "transform 0.2s ease, box-shadow 0.2s ease",
  cursor: zoomed.value ? "zoom-out" : "zoom-in",
}));
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
  overflow: hidden;
}

.lightbox-frame {
  width: 90vw;
  height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-img {
  max-width: 100%;
  max-height: 100%;
  display: block;
  touch-action: none;
  user-select: none;
}
</style>
