<template>
  <VJsoneditor
    :value="value"
    :height="height"
    :options="options"
    :attrs="$attrs"
    @input="$emit('input', $event)"
  ></VJsoneditor>
</template>

<script lang="ts">
// @ts-ignore v-jsoneditor has no types
import VJsoneditor from "v-jsoneditor";
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  components: { VJsoneditor },
  props: {
    value: {
      type: Object,
      default: () => ({}),
    },
    height: {
      type: String,
      default: "1500px",
    },
    options: {
      type: Object,
      default: () => ({}),
    },
  },
});
</script>
