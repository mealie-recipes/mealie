<template>
  <div v-if="scaledAmountDisplay" class="d-flex align-center">
    <v-row no-gutters class="d-flex flex-wrap align-center" style="font-size: larger;">
      <v-icon x-large left color="primary">
        {{ $globals.icons.bread }}
      </v-icon>
      <p class="my-0"><span class="font-weight-bold">{{ $i18n.tc("recipe.yield") }}</span><br>{{ scaledAmountDisplay }} {{ text }}</p>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
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

    const { scaledAmountDisplay } = useScaledAmount(props.yieldQuantity, props.scale);
    const text = sanitizeHTML(props.yield);

    return {
      scaledAmountDisplay,
      text,
    };
  },
});
</script>
