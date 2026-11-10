<template>
  <div
    v-if="yieldDisplay"
    class="d-flex align-center"
  >
    <v-row
      no-gutters
      class="d-flex flex-wrap align-center"
      style="font-size: larger;"
    >
      <v-icon
        size="large"
        start
        color="primary"
      >
        {{ $globals.icons.bread }}
      </v-icon>
      <p class="my-0 opacity-80">
        <span class="font-weight-bold">{{ $t("recipe.yield") }}</span><br>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <span v-html="yieldDisplay" />
      </p>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { sanitizeInlineHtml } from "~/lib/sanitize/inline";
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";

interface Props {
  yieldQuantity?: number;
  yieldText?: string | null;
  scale?: number;
  color?: string;
}
const props = withDefaults(defineProps<Props>(), {
  yieldQuantity: 0,
  yieldText: "",
  scale: 1,
  color: "accent custom-transparent",
});

const yieldDisplay = computed<string>(() => {
  const components: string[] = [];

  const { scaledAmountDisplay } = useScaledAmount(props.yieldQuantity, props.scale);
  if (scaledAmountDisplay) {
    components.push(scaledAmountDisplay);
  }

  const text = props.yieldText;
  if (text) {
    components.push(text);
  }

  return sanitizeInlineHtml(components.join(" "));
});
</script>
