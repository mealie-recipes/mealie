<template>
  <div
    ref="el"
    :class="isOverDropZone ? 'over' : ''"
  >
    <div
      v-if="isOverDropZone"
      class="overlay"
    />
    <div
      v-if="isOverDropZone"
      class="absolute text-container"
    >
      <p class="text-center drop-text">
        {{ $t("recipe.drop-image") }}
      </p>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { useDropZone } from "@vueuse/core";

defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["drop", "drop-url", "drop-unsupported"]);

const el = ref<HTMLDivElement>();

/**
 * Pulls the src out of the first <img> in a drag payload.
 *
 * Deliberately not a general HTML parser: the input is markup the browser serialized for this
 * drag, and a miss simply falls through to text/uri-list. The leading \s is what keeps it from
 * matching `data-src` and similar attributes.
 */
const IMG_SRC = /<img\b[^>]*?\ssrc\s*=\s*["']([^"']+)["']/i;

function isHttpUrl(value: string) {
  try {
    const { protocol } = new URL(value);
    return protocol === "http:" || protocol === "https:";
  }
  catch {
    return false;
  }
}

function isImageDataUrl(value: string) {
  return /^data:image\//i.test(value);
}

/**
 * Turns a base64 data: url into a file, so it can go through the ordinary upload path -- the
 * bytes are already here, and no server can fetch a data: url on our behalf.
 *
 * Only base64 payloads are handled; percent-encoded image data urls are vanishingly rare.
 */
function fileFromDataUrl(value: string) {
  const match = /^data:(image\/[\w.+-]+);base64,(.*)$/i.exec(value);
  if (!match) {
    return null;
  }

  const [, type, base64] = match;

  try {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }

    // "image/svg+xml" would give "svg+xml"; the server rejects that, but the extension it
    // reads off the name should still look like an extension.
    const extension = type.slice("image/".length).replace(/\+.*$/, "");
    return new File([bytes], `image.${extension}`, { type });
  }
  catch {
    return null;
  }
}

/**
 * An image dragged out of another browser tab carries a URL rather than a file, so there is
 * nothing to upload directly. Find the best candidate so the caller can act on it.
 */
function imageSourceFrom(dataTransfer: DataTransfer | null) {
  if (!dataTransfer) {
    return null;
  }

  // text/uri-list describes whatever was dragged, which for an image inside a link (Google
  // Images, product grids) is the link rather than the picture -- so the markup's <img> wins.
  const candidates = [
    dataTransfer.getData("text/html").match(IMG_SRC)?.[1],
    // The list may hold several URLs, and lines beginning with "#" are comments.
    ...dataTransfer.getData("text/uri-list").split("\n"),
  ]
    .map(value => value?.trim())
    .filter((value): value is string => !!value && !value.startsWith("#"))
    // Attribute values arrive HTML-escaped, and a thumbnail URL's query string is full of `&`.
    .map(value => value.replace(/&amp;/g, "&"));

  const usable = candidates.find(value => isHttpUrl(value) || isImageDataUrl(value));

  // Falling back to the first candidate lets the caller tell "nothing was dropped" apart from
  // "something was dropped that we cannot use".
  return usable ?? candidates[0] ?? null;
}

function onDrop(files: File[] | null, event: DragEvent) {
  if (files?.length) {
    emit("drop", files);
    return;
  }

  const source = imageSourceFrom(event.dataTransfer);
  if (!source) {
    return;
  }

  if (isHttpUrl(source)) {
    emit("drop-url", source);
    return;
  }

  if (isImageDataUrl(source)) {
    const file = fileFromDataUrl(source);
    if (file) {
      emit("drop", [file]);
      return;
    }
  }

  // Usually a blob: url. Those resolve only inside the origin that created them, so neither
  // this page nor the server can read the bytes -- say so rather than doing nothing.
  emit("drop-unsupported");
}

const { isOverDropZone } = useDropZone(el, (files, event) => onDrop(files, event));
</script>

<style lang="css">
.over {
  background-color: #f0f0f0;
}
.overlay {
  position: absolute;
  filter: blur(2px);
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.309);
}

.text-container {
  z-index: 10;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.drop-text {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}
</style>
