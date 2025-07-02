<template>
  <div>
    <div
      v-if="displayPreview"
      class="d-flex justify-end"
    >
      <BaseButtonGroup
        :buttons="[
          {
            icon: previewState ? $globals.icons.edit : $globals.icons.eye,
            text: previewState ? $t('general.edit') : $t('markdown-editor.preview-markdown-button-label'),
            event: 'toggle',
          },
        ]"
        @toggle="previewState = !previewState"
      />
    </div>
    <v-textarea
      v-if="!previewState"
      v-bind="textarea"
      v-model="inputVal"
      :class="label == '' ? '' : 'mt-5'"
      :label="label"
      auto-grow
      density="compact"
      rows="4"
      variant="underlined"
    />
    <SafeMarkdown
      v-else
      :source="modelValue"
    />
  </div>
</template>

<script lang="ts">
export default defineNuxtComponent({
  name: "MarkdownEditor",
  props: {
    modelValue: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      default: "",
    },
    preview: {
      type: Boolean,
      default: undefined,
    },
    displayPreview: {
      type: Boolean,
      default: true,
    },
    textarea: {
      type: Object as () => unknown,
      default: () => ({}),
    },
  },
  emits: ["update:modelValue", "input:preview"],
  setup(props, context) {
    const fallbackPreview = ref(false);
    const previewState = computed({
      get: () => {
        return props.preview ?? fallbackPreview.value;
      },
      set: (val) => {
        if (props.preview) {
          context.emit("input:preview", val);
        }
        else {
          fallbackPreview.value = val;
        }
      },
    });

    const inputVal = computed({
      get: () => {
        return props.modelValue;
      },
      set: (val) => {
        context.emit("update:modelValue", val);
      },
    });
    return {
      previewState,
      inputVal,
    };
  },
});
</script>
