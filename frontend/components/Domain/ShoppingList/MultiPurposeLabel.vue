<template>
  <v-chip v-bind="$attrs" label :color="label.color || undefined" :text-color="textColor">
    {{ label.name }}
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { MultiPurposeLabelSummary } from "~/types/api-types/recipe";

export default defineComponent({
  props: {
    label: {
      type: Object as () => MultiPurposeLabelSummary,
      required: true,
    },
  },
  setup(props) {
    const textColor = computed(() => {
      if (!props.label.color) {
        return "black";
      }

      return pickTextColorBasedOnBgColorAdvanced(props.label.color, "white", "black");
    });

    /*
    Function to pick the text color based on the background color.

    Based on -> https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
    */

    const ACCESSIBILITY_THRESHOLD = 0.179;

    function pickTextColorBasedOnBgColorAdvanced(bgColor: string, lightColor: string, darkColor: string) {
      const color = bgColor.charAt(0) === "#" ? bgColor.substring(1, 7) : bgColor;
      const r = parseInt(color.substring(0, 2), 16); // hexToR
      const g = parseInt(color.substring(2, 4), 16); // hexToG
      const b = parseInt(color.substring(4, 6), 16); // hexToB
      const uicolors = [r / 255, g / 255, b / 255];
      const c = uicolors.map((col) => {
        if (col <= 0.03928) {
          return col / 12.92;
        }
        return Math.pow((col + 0.055) / 1.055, 2.4);
      });
      const L = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
      return L > ACCESSIBILITY_THRESHOLD ? darkColor : lightColor;
    }

    return {
      textColor,
    };
  },
});
</script>