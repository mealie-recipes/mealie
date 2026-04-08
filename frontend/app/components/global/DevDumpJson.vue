<template>
  <pre>
      {{ prettyJson }}
  </pre>
</template>

<script setup lang="ts">
const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});

const prettyJson = JSON.stringify(props.data, null, 2);
</script>
