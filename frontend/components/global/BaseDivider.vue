<template>
  <v-divider :width="width" :class="color" :style="`border-width: ${thickness} !important`" />
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    width: {
      type: String,
      default: "100px",
    },
    thickness: {
      type: String,
      default: "2px",
    },
    color: {
      type: String,
      default: "accent",
    },
  },
});
</script>
