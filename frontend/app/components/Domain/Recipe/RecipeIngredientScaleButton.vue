<template>
  <v-menu
    v-if="canScale"
    v-model="menu"
    location="bottom start"
    :close-on-content-click="false"
    max-width="320"
  >
    <template #activator="{ props: menuProps }">
      <v-tooltip
        size="small"
        location="top"
        color="secondary-darken-1"
      >
        <template #activator="{ props: tooltipProps }">
          <v-btn
            v-bind="{ ...menuProps, ...tooltipProps }"
            icon
            variant="plain"
            :aria-label="$t('recipe.scale-by-ingredient')"
            class="scale-ingredient-btn"
            @click.stop
          >
            <v-icon size="small">
              {{ $globals.icons.edit }}
            </v-icon>
          </v-btn>
        </template>
        <span>{{ $t("recipe.scale-by-ingredient") }}</span>
      </v-tooltip>
    </template>
    <v-card min-width="280">
      <v-card-title class="text-subtitle-1 pb-1">
        {{ title }}
      </v-card-title>
      <v-card-subtitle v-if="originalDisplay" class="text-caption">
        {{ originalDisplay }}
      </v-card-subtitle>
      <v-card-text class="pt-2">
        <div class="d-flex align-center">
          <v-number-input
            :model-value="currentAmount"
            :precision="null"
            :min="0"
            variant="underlined"
            control-variant="hidden"
            :suffix="unitDisplay"
            @update:model-value="recalculateScale($event || 0)"
          />
          <v-tooltip
            location="end"
            color="secondary-darken-1"
          >
            <template #activator="{ props: resetTooltipProps }">
              <v-btn
                v-bind="resetTooltipProps"
                icon
                flat
                class="mx-1"
                size="small"
                :disabled="scale === 1"
                @click="scale = 1"
              >
                <v-icon>
                  {{ $globals.icons.undo }}
                </v-icon>
              </v-btn>
            </template>
            <span> {{ $t("recipe.reset-scale") }} </span>
          </v-tooltip>
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { calculateScaleFromIngredient, useScaledAmount } from "~/composables/recipes/use-scaled-amount";
import { useIngredientTextParser } from "~/composables/recipes";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

interface Props {
  ingredient: RecipeIngredient;
}

const props = defineProps<Props>();
const scale = defineModel<number>({ default: 1 });

const i18n = useI18n();
const menu = ref(false);

const baseQuantity = computed(() => {
  const q = Number(props.ingredient.quantity);
  return isNaN(q) ? 0 : q;
});

const canScale = computed(() => baseQuantity.value > 0);

const { useParsedIngredientText } = useIngredientTextParser();

const parsedOriginal = computed(() => {
  return useParsedIngredientText(props.ingredient, 1, false);
});

const parsedCurrent = computed(() => {
  return useParsedIngredientText(props.ingredient, scale.value, false);
});

const title = computed(() => {
  return parsedOriginal.value.name || props.ingredient.note || props.ingredient.title || i18n.t("recipe.ingredient");
});

const unitDisplay = computed(() => {
  return parsedCurrent.value.unit || parsedOriginal.value.unit || "";
});

const originalDisplay = computed(() => {
  const parts = [parsedOriginal.value.quantity, parsedOriginal.value.unit].filter(Boolean).join(" ");
  return parts ? i18n.t("recipe.scale-ingredient-original", { amount: parts }) : "";
});

const currentAmount = computed(() => {
  return useScaledAmount(baseQuantity.value, scale.value).scaledAmount;
});

function recalculateScale(newAmount: number) {
  const newScale = calculateScaleFromIngredient(newAmount, baseQuantity.value);
  if (newScale !== null) {
    scale.value = newScale;
  }
}
</script>

<style lang="scss" scoped>
.scale-ingredient-btn {
  opacity: 0.65;
  transition: opacity 0.2s ease-in-out;

  &:hover {
    opacity: 1;
  }
}
</style>
