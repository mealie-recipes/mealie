<template>
  <pre>
      {{ prettyJson }}
  </pre>
</template>

<script lang="ts">
export default defineNuxtComponent({
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
