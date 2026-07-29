<template>
  <ParseDialogChangeParser
    v-model="state.parser"
    :available-parsers="availableParsers"
    @update:model-value="$emit('changeParser', $event)"
    @parse="$emit('parse')"
  />
  <v-card-text class="pb-0 mb-0 d-flex flex-column ga-2">
    <div class="text-center px-8 py-4 mb-6 bg-background-darken-1 rounded-pill">
      <p class="text-h5 font-italic">
        {{ currentIng.input }}
      </p>
    </div>
    <div class="d-flex align-center pa-0 ma-0">
      <v-icon
        :color="(currentIng.confidence?.average || 0) < confidenceThreshold ? 'error' : 'success'"
      >
        {{ (currentIng.confidence?.average || 0) < confidenceThreshold ? $globals.icons.alert : $globals.icons.check }}
      </v-icon>
      <span
        class="ml-2"
        :color="currentIngHasError ? 'error-text' : 'success-text'"
      >
        {{ $t("recipe.parser.confidence-score") }}: {{ currentIng.confidence ? asPercentage(currentIng.confidence?.average!) : "" }}
      </span>
    </div>
    <RecipeIngredientEditor
      v-model="currentIng.ingredient"
      :unit-error="!!currentMissingUnit"
      :unit-error-tooltip="$t('recipe.parser.this-unit-could-not-be-parsed-automatically')"
      :food-error="!!currentMissingFood"
      :food-error-tooltip="$t('recipe.parser.this-food-could-not-be-parsed-automatically')"
    />
    <div class="d-flex flex-wrap justify-end ga-2">
      <BaseButton
        v-if="currentMissingUnit && !currentIng.ingredient.unit?.id"
        :icon="$globals.icons.units"
        color="warning"
        size="small"
        @click="$emit('createUnit')"
      >
        {{ $t("recipe.parser.missing-unit", { unit: currentMissingUnit }) }}
      </BaseButton>
      <BaseButton
        v-if="
          currentMissingUnit
            && currentIng.ingredient.unit?.id
            && currentMissingUnit.toLowerCase() != currentIng.ingredient.unit?.name.toLowerCase()
        "
        :icon="$globals.icons.units"
        color="warning"
        size="small"
        @click="$emit('aliasUnit')"
      >
        {{ $t("recipe.parser.add-text-as-alias-for-item", { text: currentMissingUnit, item: currentIng.ingredient.unit.name }) }}
      </BaseButton>
      <BaseButton
        v-if="currentMissingFood && !currentIng.ingredient.food?.id"
        :icon="$globals.icons.foods"
        color="warning"
        size="small"
        @click="$emit('createFood')"
      >
        {{ $t("recipe.parser.missing-food", { food: currentMissingFood }) }}
      </BaseButton>
      <BaseButton
        v-if="
          currentMissingFood
            && currentIng.ingredient.food?.id
            && currentMissingFood.toLowerCase() != currentIng.ingredient.food?.name.toLowerCase()
        "
        :icon="$globals.icons.foods"
        color="warning"
        size="small"
        @click="$emit('aliasFood')"
      >
        {{ $t("recipe.parser.add-text-as-alias-for-item", { text: currentMissingFood, item: currentIng.ingredient.food.name }) }}
      </BaseButton>
    </div>
  </v-card-text>
  <v-checkbox
    v-model="state.shouldDelete"
    color="error"
    hide-details
    density="compact"
    class="mt-8"
    :label="$t('recipe.parser.delete-item')"
    @update:model-value="$emit('changeShouldDelete', $event || false)"
  />
</template>

<script setup lang="ts">
import type { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import type { ParsedIngredient } from "~/lib/api/types/recipe";
import type { Parser } from "~/lib/api/user/recipes/recipe";

defineEmits<{
  parse: [];
  changeParser: [Parser];
  changeShouldDelete: [boolean];
  createUnit: [];
  createFood: [];
  aliasUnit: [];
  aliasFood: [];
}>();
const props = defineProps<{
  availableParsers: MenuItem[];
  shouldDelete: boolean;
  confidenceThreshold: number;
  currentIngHasError: string;
  currentMissingUnit: string;
  currentMissingFood: string;
  parser: Parser;
}>();

const state = reactive({
  shouldDelete: props.shouldDelete,
  parser: props.parser,
});

const currentIng = defineModel<ParsedIngredient>({
  default: () => ({
    ingredient: {},
  }),
});

function asPercentage(num: number | undefined): string {
  if (!num) {
    return "0%";
  }

  return Math.round(num * 100).toFixed(2) + "%";
}
</script>
