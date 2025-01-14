<template>
  <div v-if="yieldDisplay">
    <div class="text-center d-flex align-center">
      <div>
        <v-menu v-model="menu" :disabled="!canEditScale" offset-y top nudge-top="6" :close-on-content-click="false">
          <template #activator="{ on, attrs }">
            <v-card
              class="pa-1 px-2"
              dark
              color="secondary darken-1"
              small
              v-bind="attrs"
              :style="{ cursor: canEditScale ? '' : 'default' }"
              v-on="on"
            >
              <v-icon v-if="canEditScale" small class="mr-2">{{ $globals.icons.edit }}</v-icon>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <span v-html="yieldDisplay"></span>
            </v-card>
          </template>
          <v-card min-width="300px">
            <v-card-title class="mb-0">
              {{ $t("recipe.servings") }}
            </v-card-title>
            <v-card-text class="mt-n5">
              <div class="mt-4 d-flex align-center">
                <v-text-field v-model="yieldQuantityEditorValue" type="number" :min="0" hide-spin-buttons @input="recalculateScale(yieldQuantityEditorValue)" />
                <v-tooltip right color="secondary darken-1">
                  <template #activator="{ on, attrs }">
                    <v-btn v-bind="attrs" icon class="mx-1" small v-on="on" @click="scale = 1">
                      <v-icon>
                        {{ $globals.icons.undo }}
                      </v-icon>
                    </v-btn>
                  </template>
                  <span> {{ $t("recipe.reset-servings-count") }} </span>
                </v-tooltip>
              </div>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
      <BaseButtonGroup
        v-if="canEditScale"
        class="pl-2"
        :large="false"
        :buttons="[
          {
            icon: $globals.icons.minus,
            text: $tc('recipe.decrease-scale-label'),
            event: 'decrement',
            disabled: disableDecrement,
          },
          {
            icon: $globals.icons.createAlt,
            text: $tc('recipe.increase-scale-label'),
            event: 'increment',
          },
        ]"
        @decrement="recalculateScale(yieldQuantity - 1)"
        @increment="recalculateScale(yieldQuantity + 1)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, watch } from "@nuxtjs/composition-api";
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";

export default defineComponent({
  props: {
    value: {
      type: Number,
      required: true,
    },
    recipeServings: {
      type: Number,
      default: 0,
    },
    editScale: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { emit }) {
    const { i18n } = useContext();
    const menu = ref<boolean>(false);
    const canEditScale = computed(() => props.editScale && props.recipeServings > 0);

    const scale = computed({
      get: () => props.value,
      set: (value) => {
        const newScaleNumber = parseFloat(`${value}`);
        emit("input", isNaN(newScaleNumber) ? 0 : newScaleNumber);
      },
    });

    function recalculateScale(newYield: number) {
      if (isNaN(newYield) || newYield <= 0) {
        return;
      }

      if (props.recipeServings <= 0) {
        scale.value = 1;
      } else {
        scale.value = newYield / props.recipeServings;
      }
    }

    const recipeYieldAmount = computed(() => {
      return useScaledAmount(props.recipeServings, scale.value);
    });
    const yieldQuantity = computed(() => recipeYieldAmount.value.scaledAmount);
    const yieldDisplay = computed(() => {
      return yieldQuantity.value ? i18n.t(
        "recipe.serves-amount", { amount: recipeYieldAmount.value.scaledAmountDisplay }
      ) as string : "";
    });

    // only update yield quantity when the menu opens, so we don't override the user's input
    const yieldQuantityEditorValue = ref(recipeYieldAmount.value.scaledAmount);
    watch(
      () => menu.value,
      () => {
        if (!menu.value) {
          return;
        }

        yieldQuantityEditorValue.value = recipeYieldAmount.value.scaledAmount;
      }
    )

    const disableDecrement = computed(() => {
      return recipeYieldAmount.value.scaledAmount <= 1;
    });

    return {
      menu,
      canEditScale,
      scale,
      recalculateScale,
      yieldDisplay,
      yieldQuantity,
      yieldQuantityEditorValue,
      disableDecrement,
    };
  },
});
</script>
