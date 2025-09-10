<template>
  <BaseDialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-container class="pa-2 ma-0" style="background-color: rgb(var(--v-theme-background));">
      <BaseCardSectionTitle :title="$t('recipe.parser.ingredient-parser')">
        <div class="d-flex align-center">
          <div class="my-auto">
            {{ $t("recipe.parser.select-parser") }}
          </div>
          <BaseOverflowButton
            v-model="parser"
            :disabled="parserLoading"
            btn-class="mx-2 my-auto"
            :items="availableParsers"
          />
          <v-btn
            icon
            size="40"
            color="info"
            class="ml-auto"
            :disabled="parserLoading"
            @click="parseIngredients"
          >
            <v-icon>{{ $globals.icons.refresh }}</v-icon>
          </v-btn>
        </div>
      </BaseCardSectionTitle>
      <AppLoader v-if="parserLoading" waiting-text="" class="my-6" />
      <v-card v-else-if="!allReviewed && currentIng">
        <v-card-text class="pb-0 mb-0">
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
            :unit-error="!!currentIngUnitError"
            :unit-error-tooltip="$t('recipe.parser.this-unit-could-not-be-parsed-automatically')"
            :food-error="!!currentIngFoodError"
            :food-error-tooltip="$t('recipe.parser.this-food-could-not-be-parsed-automatically')"
          />
          <p class="pt-4 pb-0 my-0">
            {{ $t("recipe.original-text-with-value", { originalText: currentIng.input }) }}
          </p>
          <v-card-actions>
            <v-spacer />
            <BaseButton
              v-if="currentIngUnitError"
              color="warning"
              size="small"
              @click="createUnit"
            >
              {{ currentIngUnitError }}
            </BaseButton>
            <BaseButton
              v-if="currentIngFoodError"
              color="warning"
              size="small"
              @click="createFood"
            >
              {{ currentIngFoodError }}
            </BaseButton>
          </v-card-actions>
        </v-card-text>
      </v-card>
      <v-expansion-panels v-else>
        <v-card-title>{{ $t("recipe.parser.parsing-completed") }}</v-card-title>
        <v-expansion-panel>
          <v-expansion-panel-title>
            {{ $t("recipe.parser.review-parsed-ingredients") }}
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <VueDraggable
              v-model="parsedIngs"
              handle=".handle"
              :delay="250"
              :delay-on-touch-only="true"
              v-bind="{
                animation: 200,
                group: 'recipe-ingredients',
                disabled: false,
                ghostClass: 'ghost',
              }"
              @start="drag = true"
              @end="drag = false"
            >
              <TransitionGroup
                type="transition"
              >
                <RecipeIngredientEditor
                  v-for="(ingredient, index) in parsedIngs"
                  :key="index"
                  v-model="ingredient.ingredient"
                  enable-context-menu
                  class="list-group-item"
                  @delete="parsedIngs.splice(index, 1)"
                  @insert-above="insertNewIngredient(index)"
                  @insert-below="insertNewIngredient(index + 1)"
                />
              </TransitionGroup>
            </VueDraggable>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
  </BaseDialog>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import type { ParsedIngredient, RecipeIngredient } from "~/lib/api/types/recipe";
import type { Parser, } from "~/lib/api/user/recipes/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useAppInfo, useUserApi } from "~/composables/api";
import { useGlobalI18n } from "~/composables/use-global-i18n";
import { useParsingPreferences } from "~/composables/use-users/preferences";

const props = defineProps<{
  modelValue: boolean;
  ingredients: NoUndefinedField<RecipeIngredient[]>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "update:ingredients", value: NoUndefinedField<RecipeIngredient[]>): void;
}>();

const i18n = useGlobalI18n();
const api = useUserApi();
const appInfo = useAppInfo();
const drag = ref(false);

const parserPreferences = useParsingPreferences();
const parser = ref<Parser>(parserPreferences.value.parser || "nlp");
const availableParsers = computed(() => {
  return [
    {
      text: i18n.t("recipe.parser.natural-language-processor"),
      value: "nlp",
    },
    {
      text: i18n.t("recipe.parser.brute-parser"),
      value: "brute",
    },
    {
      text: i18n.t("recipe.parser.openai-parser"),
      value: "openai",
      hide: !appInfo.value?.enableOpenai,
    },
  ];
});

/**
 * If confidence of parsing is below this threshold,
 * we will prompt the user to review the parsed ingredient.
 */
const confidenceThreshold = 0.85;
const parsedIngs = ref<ParsedIngredient[]>([]);
const currentParsedIndex = ref<number>(-1);
const currentIng = ref<ParsedIngredient | null>(null);
const currentIngUnitError = ref("");
const currentIngFoodError = ref("");
const currentIngHasError = computed(() => currentIngUnitError.value || currentIngFoodError.value);
const allReviewed = computed(() => {
  return currentParsedIndex.value >= parsedIngs.value.length;
});

function shouldReview(ing: ParsedIngredient): boolean {
  console.debug(`Checking if ingredient needs review (input="${ing.input})":`, ing);

  if ((ing.confidence?.average || 0) < confidenceThreshold) {
    console.debug("Needs review due to low confidence:", ing.confidence?.average);
    return true;
  }

  const food = ing.ingredient.food;
  if (food && !food.id) {
    console.debug("Needs review due to missing food ID:", food);
    return true;
  }

  const unit = ing.ingredient.unit;
  if (unit && !unit.id) {
    console.debug("Needs review due to missing unit ID:", unit);
    return true;
  }

  console.debug("No review needed");
  return false;
}

function checkUnit(ing: ParsedIngredient) {
  if (ing.ingredient.unit?.id) {
    currentIngUnitError.value = "";
    return;
  }

  const unit = ing.ingredient.unit?.name || i18n.t("recipe.parser.no-unit");
  currentIngUnitError.value = i18n.t("recipe.parser.missing-unit", { unit }).toString();
  ing.ingredient.unit = undefined;
}

function checkFood(ing: ParsedIngredient) {
  if (ing.ingredient.food?.id) {
    currentIngFoodError.value = "";
    return;
  }
  const food = ing.ingredient.food?.name || i18n.t("recipe.parser.no-food");
  currentIngFoodError.value = i18n.t("recipe.parser.missing-food", { food }).toString();
  ing.ingredient.food = undefined;
}

function nextIngredient() {
  let nextIndex = Math.min(currentParsedIndex.value + 1, parsedIngs.value.length - 1);

  while (nextIndex < parsedIngs.value.length) {
    const current = parsedIngs.value[nextIndex];
    if (shouldReview(current)) {
      currentParsedIndex.value = nextIndex;
      currentIng.value = current;
      checkUnit(current);
      checkFood(current);
      return;
    }

    nextIndex += 1;
  }
}

const parserLoading = ref(false);
async function parseIngredients() {
  if (parserLoading.value) {
    return;
  }

  if (!props.ingredients || props.ingredients.length === 0) {
    parserLoading.value = false;
    return;
  }
  parserLoading.value = true;
  try {
    const ingsAsString = props.ingredients.map(ing => ing.display ?? "");
    const { data, error } = await api.recipes.parseIngredients(parser.value, ingsAsString);
    if (error || !data) {
      throw new Error("Failed to parse ingredients");
    }
    parsedIngs.value = data;
    currentParsedIndex.value = -1;
    nextIngredient();
  } catch (error) {
    console.error("Error parsing ingredients:", error); // TODO: flash an alert
  } finally {
    parserLoading.value = false;
  }
}

function createUnit() {
  return; // TODO: implement
}

function createFood() {
  return; // TODO: implement
}

watch(() => props.modelValue, () => {
  if (!props.modelValue) {
    return;
  }

  parseIngredients();
});

watch(parser, () => {
  parserPreferences.value.parser = parser.value;
  parseIngredients();
});

function asPercentage(num: number | undefined): string {
  if (!num) {
    return "0%";
  }

  return Math.round(num * 100).toFixed(2) + "%";
}

function insertNewIngredient(index: number) {
  const ing = {
    input: "",
    confidence: {},
    ingredient: {
      quantity: 1.0,
      referenceId: uuid4(),
    },
  } as ParsedIngredient;

  parsedIngs.value.splice(index, 0, ing);
}

</script>
