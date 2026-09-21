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

const emit = defineEmits(["drop", "drop-url"]);

const el = ref<HTMLDivElement>();

function isHttpUrl(value: string) {
  try {
    const { protocol } = new URL(value);
    return protocol === "http:" || protocol === "https:";
  }
  catch {
    return false;
  }
}

/**
 * An image dragged out of another browser tab carries a URL rather than a file, so there is
 * nothing to upload directly. Pull the URL out so the caller can have the server fetch it.
 */
function imageUrlFrom(dataTransfer: DataTransfer | null) {
  if (!dataTransfer) {
    return null;
  }

  // text/uri-list may hold several URLs, and lines beginning with "#" are comments.
  const uri = dataTransfer
    .getData("text/uri-list")
    .split("\n")
    .map(line => line.trim())
    .find(line => line && !line.startsWith("#"));

  if (uri && isHttpUrl(uri)) {
    return uri;
  }

  // Some sources only offer the dragged element's markup. Read the attribute rather than
  // `img.src`, which the parser would resolve against our own origin.
  const html = dataTransfer.getData("text/html");
  if (html) {
    const src = new DOMParser().parseFromString(html, "text/html").querySelector("img")?.getAttribute("src");
    if (src && isHttpUrl(src)) {
      return src;
    }
  }

  return null;
}

function onDrop(files: File[] | null, event: DragEvent) {
  if (files?.length) {
    emit("drop", files);
    return;
  }

  const url = imageUrlFrom(event.dataTransfer);
  if (url) {
    emit("drop-url", url);
  }
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
