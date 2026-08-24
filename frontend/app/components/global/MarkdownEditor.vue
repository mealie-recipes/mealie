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
      v-model="modelValue"
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

<script setup lang="ts">
const props = defineProps({
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
});

const emit = defineEmits<{
  (e: "input:preview", value: boolean): void;
}>();

const modelValue = defineModel<string>("modelValue");

const fallbackPreview = ref(false);
const previewState = computed({
  get: () => props.preview ?? fallbackPreview.value,
  set: (val: boolean) => {
    if (props.preview) {
      emit("input:preview", val);
    }
    else {
      fallbackPreview.value = val;
    }
  },
});
</script>
