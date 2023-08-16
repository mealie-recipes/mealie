<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <v-tooltip v-if="!isEditMode && recipe.recipeYield" small top color="secondary darken-1">
      <template #activator="{ on, attrs }">
        <RecipeScaleEditButton
          v-model.number="scaleValue"
          v-bind="attrs"
          :recipe-yield="recipe.recipeYield"
          :basic-yield="basicYield"
          :scaled-yield="scaledYield"
          :edit-scale="!recipe.settings.disableAmount && !isEditMode"
          v-on="on"
        />
      </template>
      <span> {{ $t("recipe.edit-scale") }} </span>
    </v-tooltip>
    <v-spacer></v-spacer>

    <RecipeRating
      v-if="landscape && $vuetify.breakpoint.smAndUp"
      :key="recipe.slug"
      v-model="recipe.rating"
      :name="recipe.name"
      :slug="recipe.slug"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { useFraction } from "~/composables/recipes";

export default defineComponent({
  components: {
    RecipeScaleEditButton,
    RecipeRating,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    landscape: {
      type: Boolean,
      default: false,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props, { emit }) {
    const { isEditMode } = usePageState(props.recipe.slug);
    const { frac } = useFraction();

    const scaleValue = computed<number>({
      get() {
        return props.scale;
      },
      set(val) {
        emit("update:scale", val);
      },
    });

    const matchMixedFraction = /(?:[1-9]\s[1-9]\d*|0)\/[1-9]\d*/;
    const matchFraction = /(?:[1-9]\d*|0)\/[1-9]\d*/;
    const matchDecimal = /(\d+.\d+)|(.\d+)/;
    const matchInt = /\d+/;

    function parseYieldString(yieldString: string | null, scale: number) {
      if (!yieldString) {
        return "";
      }

      // attempt to parse the yield into a mixed fraction, regular fraction, decimal, or integer
      let match: string | null = null;
      let servings: number | null = null;
      let isFraction = false;

      if (!(match && servings)) {
        const mixedFractionMatch = yieldString?.match(matchMixedFraction);
        if (mixedFractionMatch?.length) {
          isFraction = true;
          match = mixedFractionMatch[0];

          const mixedSplit = match.split(/\s/);
          const wholeNumber = parseInt(mixedSplit[0]);
          const fraction = mixedSplit[1];

          const fractionSplit = fraction.split("/");
          const numerator = parseInt(fractionSplit[0]);
          const denominator = parseInt(fractionSplit[1]);

          if (denominator === 0) {
            return yieldString;  // if the denominator is zero, just give up
          }
          else {
            servings = wholeNumber + (numerator / denominator);
          }
        }
      }

      if (!(match && servings)) {
        const fractionMatch = yieldString?.match(matchFraction);
        if (fractionMatch?.length) {
          isFraction = true;
          match = fractionMatch[0];

          const fractionSplit = match.split("/");
          const numerator = parseInt(fractionSplit[0]);
          const denominator = parseInt(fractionSplit[1]);

          if (denominator === 0) {
            return yieldString;  // if the denominator is zero, just give up
          }
          else {
            servings = numerator / denominator;
          }
        }
      }

      if (!(match && servings)) {
        const decimalMatch = yieldString?.match(matchDecimal);
        if (decimalMatch?.length) {
          match = decimalMatch[0];
          servings = parseFloat(match);
        }
      }

      if (!(match && servings)) {
        const intMatch = yieldString?.match(matchInt);
        if (intMatch?.length) {
          match = intMatch[0];
          servings = parseInt(intMatch[0]);
        }
      }

      if (match && servings) {
        const val = servings * scale;
        let valString = ""

        if (!Number.isInteger(val)) {
          if (isFraction) {
            const fraction = frac(val, 10, true);

            if (fraction[0] !== undefined && fraction[0] > 0) {
              valString += fraction[0];
            }

            if (fraction[1] > 0) {
              valString += ` ${fraction[1]}/${fraction[2]}`;
            }

            if (!valString) {
              return yieldString;  // this only happens with very weird or small fractions
            }

          } else {
            valString = (Math.round(val * 1000) / 1000).toString();
          }
        } else {
          valString = val.toString();
        }

        return yieldString.replace(match, valString);
      } else {
        return yieldString;
      }
    }

    const scaledYield = computed(() => {
      return parseYieldString(props.recipe.recipeYield, scaleValue.value);
    });

    const basicYield = computed(() => {
      return parseYieldString(props.recipe.recipeYield, 1);
    });

    return {
      scaleValue,
      basicYield,
      scaledYield,
      isEditMode,
    };
  },
});
</script>
