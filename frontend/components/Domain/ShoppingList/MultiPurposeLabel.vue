<template>
  <v-chip v-bind="$attrs" label :color="label.color || undefined" :text-color="textColor">
    <span style="max-width: 100%; overflow: hidden; text-overflow: ellipsis;">
      {{ label.name }}
    </span>
  </v-chip>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
// @ts-ignore missing color types
import Color from "@sphinxxxx/color-conversion";
import { MultiPurposeLabelSummary } from "~/lib/api/types/recipe";


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
      try {
        const color = new Color(bgColor);

        // if opacity is less than 0.3 always return dark color
        if (color._rgba[3] < 0.3) {
          return darkColor;
        }

        const uicolors = [color._rgba[0] / 255, color._rgba[1] / 255, color._rgba[2] / 255];
        const c = uicolors.map((col) => {
          if (col <= 0.03928) {
            return col / 12.92;
          }
          return Math.pow((col + 0.055) / 1.055, 2.4);
        });
        const L = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
        return L > ACCESSIBILITY_THRESHOLD ? darkColor : lightColor;
      } catch (error) {
        console.warn(error);
        return "black";
      }
    }

    return {
      textColor,
    };
  },
});
</script>
