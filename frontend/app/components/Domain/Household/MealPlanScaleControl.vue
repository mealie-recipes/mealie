<template>
  <div class="text-center d-flex align-center">
    <v-menu
      v-model="menu"
      offset-y
      top
      nudge-top="6"
      :close-on-content-click="false"
    >
      <template #activator="{ props: activatorProps }">
        <v-tooltip
          size="small"
          location="top"
          color="secondary-darken-1"
        >
          <template #activator="{ props: tooltipProps }">
            <v-card
              class="pa-0 px-2 d-flex align-center"
              dark
              color="secondary-darken-1"
              style="cursor: pointer"
              v-bind="{ ...activatorProps, ...tooltipProps }"
            >
              <v-icon size="x-small" class="mr-1">
                {{ $globals.icons.edit }}
              </v-icon>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <span class="text-caption" v-html="yieldDisplay" />
            </v-card>
          </template>
          <span>{{ $t("recipe.edit-scale") }}</span>
        </v-tooltip>
      </template>

      <v-card min-width="300px">
        <v-card-title class="mb-0">
          {{ $t("recipe.servings") }}
        </v-card-title>
        <v-card-text class="mt-n5">
          <div class="mt-4 d-flex align-center">
            <v-number-input
              :model-value="yieldQuantity"
              :precision="null"
              :min="0"
              variant="underlined"
              control-variant="hidden"
              @update:model-value="recalculateScale($event || 0)"
            />
            <v-tooltip
              location="end"
              color="secondary-darken-1"
            >
              <template #activator="{ props: resetProps }">
                <v-btn
                  v-bind="resetProps"
                  icon
                  flat
                  class="mx-1"
                  size="small"
                  @click="localScale = 1"
                >
                  <v-icon>{{ $globals.icons.undo }}</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("recipe.reset-servings-count") }}</span>
            </v-tooltip>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>

    <v-btn
      icon
      size="x-small"
      variant="plain"
      :disabled="yieldQuantity <= 1"
      class="ml-1"
      @click="recalculateScale(yieldQuantity - 1)"
    >
      <v-icon size="small">
        {{ $globals.icons.minus }}
      </v-icon>
    </v-btn>
    <v-btn
      icon
      size="x-small"
      variant="plain"
      class="ml-1"
      @click="recalculateScale(yieldQuantity + 1)"
    >
      <v-icon size="small">
        {{ $globals.icons.createAlt }}
      </v-icon>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import type { useMealplans } from "~/composables/use-group-mealplan";

const props = defineProps<{
  meal: ReadPlanEntry;
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const i18n = useI18n();
const menu = ref(false);

// Use actual recipe servings; fall back to 1 so the display always renders
const recipeServings = computed(() => {
  return props.meal.recipe?.recipeServings || props.meal.recipe?.recipeYieldQuantity || 1;
});

const localScale = ref(props.meal.recipeScale ?? 1);

watch(
  () => props.meal.recipeScale,
  (val) => { localScale.value = val ?? 1; },
);

const recipeYieldAmount = computed(() => useScaledAmount(recipeServings.value, localScale.value));
const yieldQuantity = computed(() => recipeYieldAmount.value.scaledAmount);
const yieldDisplay = computed(() =>
  yieldQuantity.value
    ? i18n.t("recipe.serves-amount", { amount: recipeYieldAmount.value.scaledAmountDisplay }) as string
    : "",
);

function recalculateScale(newYield: number) {
  if (isNaN(newYield) || newYield <= 0) return;
  localScale.value = recipeServings.value > 0 ? newYield / recipeServings.value : 1;
}

let saveTimer: ReturnType<typeof setTimeout> | null = null;

watch(localScale, (newScale) => {
  if (newScale === (props.meal.recipeScale ?? 1)) return;
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    props.actions.updateOne({ ...props.meal, recipeScale: newScale });
  }, 400);
});
</script>
