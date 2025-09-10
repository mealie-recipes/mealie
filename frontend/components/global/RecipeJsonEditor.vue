<template>
  <JsonEditorVue
    :model-value="modelValue"
    v-bind="$attrs"
    :style="{ height }"
    :stringified="false"
    @change="onChange"
  />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import JsonEditorVue from "json-editor-vue";

export default defineComponent({
  name: "RecipeJsonEditor",
  components: { JsonEditorVue },
  props: {
    modelValue: {
      type: Object,
      default: () => ({}),
    },
    height: {
      type: String,
      default: "1500px",
    },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    function parseEvent(event: any): object {
      if (!event) {
        return props.modelValue || {};
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
        return props.modelValue || {};
      }
    }
    function onChange(event: any) {
      const parsed = parseEvent(event);
      if (parsed !== props.modelValue) {
        emit("update:modelValue", parsed);
      }
    }
    return {
      onChange,
    };
  },
});
</script>
