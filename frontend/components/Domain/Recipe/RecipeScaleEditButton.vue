<template>
  <div v-if="yieldDisplay">
    <div class="text-center d-flex align-center">
      <div>
        <v-menu
          v-model="menu"
          :disabled="!canEditScale"
          offset-y
          top
          nudge-top="6"
          :close-on-content-click="false"
        >
          <template #activator="{ props }">
            <v-tooltip
              v-if="canEditScale"
              size="small"
              top
              color="secondary-darken-1"
            >
              <template #activator="{ props: tooltipProps }">
                <v-card
                  class="pa-1 px-2"
                  dark
                  color="secondary-darken-1"
                  size="small"
                  v-bind="{ ...props, ...tooltipProps }"
                  :style="{ cursor: canEditScale ? '' : 'default' }"
                >
                  <v-icon
                    v-if="canEditScale"
                    size="small"
                    class="mr-2"
                  >
                    {{ $globals.icons.edit }}
                  </v-icon>
                  <!-- eslint-disable-next-line vue/no-v-html -->
                  <span v-html="yieldDisplay" />
                </v-card>
              </template>
              <span> {{ $t("recipe.edit-scale") }} </span>
            </v-tooltip>
            <v-card
              v-else
              class="pa-1 px-2"
              dark
              color="secondary-darken-1"
              size="small"
              v-bind="props"
              :style="{ cursor: canEditScale ? '' : 'default' }"
            >
              <v-icon
                v-if="canEditScale"
                size="small"
                class="mr-2"
              >
                {{ $globals.icons.edit }}
              </v-icon>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <span v-html="yieldDisplay" />
            </v-card>
          </template>
          <v-card min-width="300px">
            <v-card-title class="mb-0">
              {{ $t("recipe.servings") }}
            </v-card-title>
            <v-card-text class="mt-n5">
              <div class="mt-4 d-flex align-center">
                <v-text-field
                  :model-value="yieldQuantity"
                  type="number"
                  :min="0"
                  variant="underlined"
                  hide-spin-buttons
                  @update:model-value="recalculateScale(parseFloat($event) || 0)"
                />
                <v-tooltip
                  end
                  color="secondary-darken-1"
                >
                  <template #activator="{ props }">
                    <v-btn
                      v-bind="props"
                      icon
                      flat
                      class="mx-1"
                      size="small"
                      @click="scale = 1"
                    >
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
            text: $t('recipe.decrease-scale-label'),
            event: 'decrement',
            disabled: disableDecrement,
          },
          {
            icon: $globals.icons.createAlt,
            text: $t('recipe.increase-scale-label'),
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
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";

export default defineNuxtComponent({
  props: {
    modelValue: {
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
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const i18n = useI18n();
    const menu = ref<boolean>(false);
    const canEditScale = computed(() => props.editScale && props.recipeServings > 0);

    const scale = computed({
      get: () => props.modelValue,
      set: (value) => {
        const newScaleNumber = parseFloat(`${value}`);
        emit("update:modelValue", isNaN(newScaleNumber) ? 0 : newScaleNumber);
      },
    });

    function recalculateScale(newYield: number) {
      if (isNaN(newYield) || newYield <= 0) {
        return;
      }

      if (props.recipeServings <= 0) {
        scale.value = 1;
      }
      else {
        scale.value = newYield / props.recipeServings;
      }
    }

    const recipeYieldAmount = computed(() => {
      return useScaledAmount(props.recipeServings, scale.value);
    });
    const yieldQuantity = computed(() => recipeYieldAmount.value.scaledAmount);
    const yieldDisplay = computed(() => {
      return yieldQuantity.value
        ? i18n.t(
          "recipe.serves-amount", { amount: recipeYieldAmount.value.scaledAmountDisplay },
        ) as string
        : "";
    });

    const disableDecrement = computed(() => {
      return yieldQuantity.value <= 1;
    });

    return {
      menu,
      canEditScale,
      scale,
      recalculateScale,
      yieldDisplay,
      yieldQuantity,
      disableDecrement,
    };
  },
});
</script>
