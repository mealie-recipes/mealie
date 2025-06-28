<template>
  <v-chip
    v-bind="$attrs"
    label
    variant="flat"
    :color="label.color || undefined"
    :text-color="textColor"
  >
    <span style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
      {{ label.name }}
    </span>
  </v-chip>
</template>

<script lang="ts">
import { getTextColor } from "~/composables/use-text-color";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/recipe";

export default defineNuxtComponent({
  props: {
    label: {
      type: Object as () => MultiPurposeLabelSummary,
      required: true,
    },
  },
  setup(props) {
    const textColor = computed(() => getTextColor(props.label.color));

    return {
      textColor,
    };
  },
});
</script>
