<template>
  <div v-html="markup"></div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
export default defineComponent({
  props: {
    markup: {
      type: String,
      required: true,
    },
  },
});
</script>
