<template>
  <pre>
      {{ prettyJson }}
  </pre>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const prettyJson = JSON.stringify(props.data, null, 2);

    return {
      prettyJson,
    };
  },
});
</script>