<template>
  <div v-if="scaledAmount" class="d-flex align-center">
    <v-row no-gutters class="d-flex flex-wrap align-center" style="font-size: larger;">
      <v-icon x-large left color="primary">
        {{ $globals.icons.bread }}
      </v-icon>
      <p class="my-0">
        <span class="font-weight-bold">{{ $i18n.tc("recipe.yield") }}</span><br>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <span v-html="scaledAmount"></span> {{ text }}
      </p>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";
import DOMPurify from "dompurify";
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";

export default defineComponent({
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
      default: "accent custom-transparent"
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
      const {scaledAmountDisplay} =  useScaledAmount(props.yieldQuantity, props.scale);
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
