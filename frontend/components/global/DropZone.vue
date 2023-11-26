<template>
  <div ref="el" :class="isOverDropZone ? 'over' : ''">
    <div v-if="isOverDropZone" class="overlay"></div>
    <div v-if="isOverDropZone" class="absolute text-container">
      <p class="text-center drop-text"> {{ $t("recipe.drop-image") }} </p>
    </div>
    <slot></slot>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useDropZone } from "@vueuse/core";

export default defineComponent({
  setup(_, context) {
    const el = ref<HTMLDivElement>();

    function onDrop(files: File[]) {
      context.emit("drop", files);
    }

    // @ts-ignore - This should work?
    const { isOverDropZone } = useDropZone(el, onDrop);

    return { el, isOverDropZone };
  },
});
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
