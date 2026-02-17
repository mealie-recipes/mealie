<template>
  <v-chip
    v-bind="$attrs"
    label
    variant="flat"
    :color="label.color || undefined"
  >
    <span style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
      {{ label.name }}
    </span>
  </v-chip>
</template>

<script lang="ts">
import type { MultiPurposeLabelSummary } from "~/lib/api/types/recipe";

export default defineNuxtComponent({
  props: {
    label: {
      type: Object as () => MultiPurposeLabelSummary,
      required: true,
    },
  },
});
</script>
