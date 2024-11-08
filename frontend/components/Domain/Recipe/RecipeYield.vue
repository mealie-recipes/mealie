<template>
  <div v-if="displayText" class="d-flex justify-space-between align-center pt-2">
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
import { useRecipeYield } from "~/composables/recipes/use-recipe-yield";

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
    const displayText = computed(() => {
      if (!(props.yieldQuantity || props.yield)) {
        return "";
      }

      const { yieldDisplay } = useRecipeYield(props.yieldQuantity, "", props.scale);

      return i18n.t("recipe.yields-amount-with-text", {
        amount: yieldDisplay,
        text: props.yield,
      });
    });

    return {
      displayText,
    };
  },
});
</script>
