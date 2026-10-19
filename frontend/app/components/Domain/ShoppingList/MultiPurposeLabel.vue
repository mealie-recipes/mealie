<template>
  <v-chip
    v-bind="$attrs"
    label
    variant="flat"
    :color="label.color || undefined"
    :style="textStyle"
  >
    <span style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
      {{ label.name }}
    </span>
  </v-chip>
</template>

<script setup lang="ts">
import type { CSSProperties } from "vue";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/recipe";

import { textColorForBackground } from "~/lib/labels/text-color";

const props = defineProps<{
  label: MultiPurposeLabelSummary;
}>();

const textStyle = computed(() => {
  const color = textColorForBackground(props.label.color);
  return color ? ({ color } as CSSProperties) : undefined;
});
</script>
