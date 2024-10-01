<template>
  <v-chip v-bind="$attrs" label :color="label.color || undefined" :text-color="textColor">
    <span style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
      {{ label.name }}
    </span>
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { getTextColor } from "~/composables/use-text-color";
import { MultiPurposeLabelSummary } from "~/lib/api/types/recipe";


export default defineComponent({
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
