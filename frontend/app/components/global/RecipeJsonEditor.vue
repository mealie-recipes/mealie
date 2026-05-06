<template>
  <JsonEditorVue
    :model-value="modelValue"
    v-bind="$attrs"
    :style="{ height }"
    :stringified="false"
    @change="onChange"
  />
</template>

<script setup lang="ts">
import JsonEditorVue from "json-editor-vue";

const modelValue = defineModel<object>("modelValue", { default: () => ({}) });
defineProps({
  height: {
    type: String,
    default: "1500px",
  },
});

function parseEvent(event: any): object {
  if (!event) {
    return modelValue.value || {};
  }
  try {
    if (event.json) {
      return event.json;
    }
    else if (event.text) {
      return JSON.parse(event.text);
    }
    else {
      return event;
    }
  }
  catch {
    return modelValue.value || {};
  }
}
function onChange(event: any) {
  const parsed = parseEvent(event);
  if (parsed !== modelValue.value) {
    modelValue.value = parsed;
  }
}
</script>
