<template>
  <div
    v-if="scaledAmount"
    class="d-flex align-center"
  >
    <v-row
      no-gutters
      class="d-flex flex-wrap align-center"
      style="font-size: larger;"
    >
      <v-icon
        size="x-large"
        start
        color="primary"
      >
        {{ $globals.icons.bread }}
      </v-icon>
      <p class="my-0 opacity-80">
        <span class="font-weight-bold">{{ $t("recipe.yield") }}</span><br>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <span v-html="scaledAmount" /> {{ text }}
      </p>
    </v-row>
  </div>
</template>

<script lang="ts">
import DOMPurify from "dompurify";
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";

export default defineNuxtComponent({
  props: {
    yieldQuantity: {
      type: Number,
      default: 0,
    },
    yield: {
      type: String,
      default: "",
    },
    scale: {
      type: Number,
      default: 1,
    },
    color: {
      type: String,
      default: "accent custom-transparent",
    },
  },
  setup(props) {
    function sanitizeHTML(rawHtml: string) {
      return DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
        ALLOWED_TAGS: ["strong", "sup"],
      });
    }

    const scaledAmount = computed(() => {
      const { scaledAmountDisplay } = useScaledAmount(props.yieldQuantity, props.scale);
      return scaledAmountDisplay;
    });
    const text = sanitizeHTML(props.yield);

    return {
      scaledAmount,
      text,
    };
  },
});
</script>
