<template>
  <VJsoneditor
    :value="value"
    height="1500px"
    :options="options"
    :attrs="$attrs"
    @input="$emit('input', $event)"
  ></VJsoneditor>
</template>

<script lang="ts">
// @ts-ignore
import VJsoneditor from "v-jsoneditor";
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  components: { VJsoneditor },
  props: {
    value: {
      type: Object,
      default: () => ({}),
    },
    options: {
      type: Object,
      default: () => ({}),
    },
  },
});
</script>

