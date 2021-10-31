<template>
  <VJsoneditor v-model="value" height="1500px" :options="options" :attrs="$attrs"></VJsoneditor>
</template>

<script>
import VJsoneditor from "v-jsoneditor";

export default {
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
};
</script>

