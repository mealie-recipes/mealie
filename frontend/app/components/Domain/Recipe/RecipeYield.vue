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
        <SafeInlineHtml :html="yieldDisplay" />
      </p>
    </v-row>
  </div>
</template>

<script setup lang="ts">
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

/**
 * The text may repeat the structured quantity, e.g. "60 servings" beside quantity 60. Strip only
 * a leading copy of the quantity; numbers later in the text are left alone.
 */
function stripLeadingQuantity(text: string, quantity: number): string {
  if (!quantity) {
    return text;
  }

  const match = /^\s*(\d+(?:\.\d+)?)(?=\s|$)/.exec(text);
  if (!match || Number(match[1]) !== quantity) {
    return text;
  }

  return text.slice(match[0].length).trimStart();
}

const yieldDisplay = computed<string>(() => {
  const components: string[] = [];

  const { scaledAmountDisplay } = useScaledAmount(props.yieldQuantity, props.scale);
  if (scaledAmountDisplay) {
    components.push(scaledAmountDisplay);
  }

  const text = props.yieldText;
  if (text) {
    const strippedText = stripLeadingQuantity(text, props.yieldQuantity);
    if (strippedText) {
      components.push(strippedText);
    }
  }

  return components.join(" ");
});
</script>
