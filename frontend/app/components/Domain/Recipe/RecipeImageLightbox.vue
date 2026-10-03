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
          :key="imageUrl"
          :src="imageUrl"
          :alt="imageAlt"
          :class="['lightbox-img', cursorClass]"
          draggable="false"
          :style="imgStyle"
          @load="onImageLoad"
          @click="onImageClick"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerCancel"
        >
      </div>
      <v-btn
        v-if="showNav && canPrev && !zoomed"
        icon
        variant="text"
        class="lightbox-nav lightbox-prev"
        :aria-label="$t('recipe.previous-image')"
        @click.stop="goPrev"
      >
        <v-icon>{{ $globals.icons.chevronLeft }}</v-icon>
      </v-btn>
      <v-btn
        v-if="showNav && canNext && !zoomed"
        icon
        variant="text"
        class="lightbox-nav lightbox-next"
        :aria-label="$t('recipe.next-image')"
        @click.stop="goNext"
      >
        <v-icon>{{ $globals.icons.chevronRight }}</v-icon>
      </v-btn>
      <div
        v-if="showNav"
        class="lightbox-caption"
        :style="{ backgroundColor: captionBg, color: captionColor }"
      >
        {{ captionText }}
      </div>
      <v-btn
        icon
        variant="text"
        class="lightbox-close"
        :aria-label="$t('general.close')"
        @click.stop="model = false"
      >
        <v-icon>{{ $globals.icons.close }}</v-icon>
      </v-btn>
    </div>
  </v-dialog>
</template>

<script setup lang="ts">
import { useTheme } from "vuetify";
import { canGoNext, canGoPrev } from "~/composables/recipe-page/use-recipe-lightbox-items";
import type { LightboxItem } from "~/composables/recipe-page/use-recipe-lightbox-items";

interface Props {
  items: LightboxItem[];
}

const props = defineProps<Props>();
const model = defineModel<boolean>({ required: true });
const index = defineModel<number>("index", { default: 0 });

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

const captionBg = computed(() =>
  isDark.value ? "rgba(255, 255, 255, 0.85)" : "rgba(0, 0, 0, 0.65)",
);
const captionColor = computed(() =>
  isDark.value ? "rgba(0, 0, 0, 0.87)" : "rgba(255, 255, 255, 0.95)",
);

// ===============================================================
// Gallery navigation

const total = computed(() => props.items.length);
const showNav = computed(() => total.value > 1);
const currentItem = computed<LightboxItem | undefined>(() => props.items[index.value]);
const imageUrl = computed(() => currentItem.value?.src);
const imageAlt = computed(() => currentItem.value?.alt);

const canPrev = computed(() => canGoPrev(index.value));
const canNext = computed(() => canGoNext(index.value, total.value));

const captionText = computed(() => {
  const position = `${index.value + 1} / ${total.value}`;
  return currentItem.value?.label ? `${currentItem.value.label} · ${position}` : position;
});

function goPrev() {
  if (canPrev.value) {
    index.value -= 1;
  }
}

function goNext() {
  if (canNext.value) {
    index.value += 1;
  }
}

function preloadImage(src?: string) {
  if (!src || typeof Image === "undefined") {
    return;
  }
  const img = new Image();
  img.src = src;
}

watch(index, (i) => {
  preloadImage(props.items[i - 1]?.src);
  preloadImage(props.items[i + 1]?.src);
}, { immediate: true });

// ===============================================================
// Keyboard navigation (only while the dialog is open)

function isTextInputTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false;
  }
  return target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable;
}

// Registered on window in the capture phase so we intercept the key before the browser's
// native scroll-the-page behavior can act on it; without preventDefault, ArrowLeft/ArrowRight
// fall through to native horizontal scroll of the underlying page since Vuetify's dialog only
// moves focus onto a plain, non-scrollable wrapper (and only after its open transition ends).
function onKeydown(event: KeyboardEvent) {
  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
    return;
  }
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
    return;
  }
  if (isTextInputTarget(event.target)) {
    return;
  }
  if (total.value <= 1) {
    return;
  }

  event.preventDefault();

  if (event.key === "ArrowLeft") {
    goPrev();
  }
  else {
    goNext();
  }
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
  window.removeEventListener("keydown", onKeydown, true);
});

const renderedSize = computed(() => {
  if (!naturalSize.w || !naturalSize.h || !frameSize.w || !frameSize.h) {
    return null;
  }

  const scale = Math.min(frameSize.w / naturalSize.w, frameSize.h / naturalSize.h);
  return { width: naturalSize.w * scale, height: naturalSize.h * scale };
});

const ZOOM_SCALE = 2;

const zoomed = ref(false);
const pan = reactive({ x: 0, y: 0 });
const dragging = ref(false);
const dragMoved = ref(false);
let dragStart = { x: 0, y: 0, panX: 0, panY: 0 };

// Keep the zoomed image overlapping its frame: at most half the overhang in each
// direction, so it can never be dragged completely out of view.
function applyPan(x: number, y: number) {
  const limitX = renderedSize.value
    ? Math.max(0, (renderedSize.value.width * ZOOM_SCALE - frameSize.w) / 2)
    : 0;
  const limitY = renderedSize.value
    ? Math.max(0, (renderedSize.value.height * ZOOM_SCALE - frameSize.h) / 2)
    : 0;

  pan.x = Math.min(Math.max(x, -limitX), limitX);
  pan.y = Math.min(Math.max(y, -limitY), limitY);
}

function resetZoom() {
  zoomed.value = false;
  pan.x = 0;
  pan.y = 0;
}

// `immediate: true` because both callers mount this component with `v-if` gated on the
// same flag as the `v-model` (e.g. `v-if="lightboxOpen" v-model="lightboxOpen"`), so the
// component is always created with `model` already `true` — a non-immediate watch would
// never observe that initial open and the keydown listener would never get attached.
watch(model, (open) => {
  if (open) {
    window.addEventListener("keydown", onKeydown, true);
  }
  else {
    window.removeEventListener("keydown", onKeydown, true);
    resetZoom();
  }
}, { immediate: true });

// Navigating within an open gallery must drop any zoom/pan from the previous image and
// let the freshly (re)mounted, keyed <img> establish its own natural/frame size, rather
// than carrying over stale values that would flash the wrong framing for a moment.
watch(index, () => {
  resetZoom();
  naturalSize.w = 0;
  naturalSize.h = 0;
  frameSize.w = 0;
  frameSize.h = 0;
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

// ===============================================================
// Pointer input: drag-to-pan while zoomed, swipe-to-navigate while not (touch/pen only)

const SWIPE_THRESHOLD = 50;
let swipeStart: { x: number; y: number } | null = null;

function onPointerDown(event: PointerEvent) {
  event.stopPropagation();

  if (zoomed.value) {
    dragging.value = true;
    dragMoved.value = false;
    dragStart = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y };
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
    return;
  }

  if (event.pointerType === "touch" || event.pointerType === "pen") {
    swipeStart = { x: event.clientX, y: event.clientY };
    dragMoved.value = false;
  }
}

function onPointerMove(event: PointerEvent) {
  if (dragging.value) {
    const dx = event.clientX - dragStart.x;
    const dy = event.clientY - dragStart.y;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      dragMoved.value = true;
    }
    applyPan(dragStart.panX + dx, dragStart.panY + dy);
    return;
  }

  if (swipeStart) {
    const dx = event.clientX - swipeStart.x;
    const dy = event.clientY - swipeStart.y;
    // Mark the gesture as a drag once it's clearly horizontal so the eventual pointerup
    // doesn't also fire onImageClick's zoom toggle.
    if (Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy)) {
      dragMoved.value = true;
    }
  }
}

function onPointerUp(event: PointerEvent) {
  event.stopPropagation();
  dragging.value = false;

  if (swipeStart) {
    const dx = event.clientX - swipeStart.x;
    const dy = event.clientY - swipeStart.y;
    swipeStart = null;

    if (Math.abs(dx) >= SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) {
        goNext();
      }
      else {
        goPrev();
      }
    }
  }
}

function onPointerCancel() {
  dragging.value = false;
  swipeStart = null;
}

const cursorClass = computed(() => {
  if (!zoomed.value) {
    return "";
  }
  return dragging.value ? "grabbing" : "grab";
});

const imgStyle = computed(() => ({
  ...(renderedSize.value
    ? { width: `${renderedSize.value.width}px`, height: `${renderedSize.value.height}px` }
    : {}),
  boxShadow: imageShadow.value,
  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoomed.value ? ZOOM_SCALE : 1})`,
  transition: dragging.value ? "none" : "transform 0.2s ease, box-shadow 0.2s ease",
  cursor: zoomed.value ? undefined : "zoom-in",
}));
</script>

<style scoped>
.lightbox-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 100%, not 100vw/100vh: this is Vuetify's v-overlay__content, whose content box shrinks
     by its scroll-lock scrollbar-offset padding. Viewport units ignore that padding and
     overflow the parent by exactly the padding amount, producing a spurious h-scrollbar. */
  width: 100%;
  height: 100%;
  cursor: zoom-out;
  transition: background-color 0.2s ease;
  overflow: hidden;
}

.lightbox-close {
  position: absolute;
  top: 12px;
  right: 12px;
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.lightbox-nav:hover,
.lightbox-nav:focus-visible {
  opacity: 1;
}

.lightbox-prev {
  left: 12px;
}

.lightbox-next {
  right: 12px;
}

.lightbox-caption {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 0.875rem;
  white-space: nowrap;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
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

.lightbox-img.grab {
  cursor: grab;
}

.lightbox-img.grabbing {
  cursor: grabbing;
}
</style>
