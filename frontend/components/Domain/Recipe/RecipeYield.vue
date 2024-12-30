<template>
  <div v-if="displayText" class="d-flex justify-space-between align-center">
    <v-chip
      :small="$vuetify.breakpoint.smAndDown"
      label
      :color="color"
    >
      <v-icon left>
        {{ $globals.icons.potSteam }}
      </v-icon>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <span v-html="displayText"></span>
    </v-chip>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
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
    const { i18n } = useContext();

    function sanitizeHTML(rawHtml: string) {
      return DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
        ALLOWED_TAGS: ["strong", "sup"],
      });
    }

    const displayText = computed(() => {
      if (!(props.yieldQuantity || props.yield)) {
        return "";
      }

      const { scaledAmountDisplay } = useScaledAmount(props.yieldQuantity, props.scale);

      return i18n.t("recipe.yields-amount-with-text", {
        amount: scaledAmountDisplay,
        text: sanitizeHTML(props.yield),
      }) as string;
    });

    return {
      displayText,
    };
  },
});
</script>
