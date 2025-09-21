<template>
  <BaseDialog
    :model-value="modelValue"
    :title="$t('recipe.parse-ingredients')"
    :icon="$globals.icons.fileSign"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-container class="pa-2 ma-0" style="background-color: rgb(var(--v-theme-background));">
      <BaseCardSectionTitle :title="$t('recipe.parser.ingredient-parser')">
        <div v-if="!state.allReviewed" class="mb-4">
          <p>{{ $t("recipe.parser.ingredient-parser-description") }}</p>
          <p>{{ $t("recipe.parser.ingredient-parser-final-review-description") }}</p>
        </div>
        <div class="d-flex flex-wrap align-center">
          <div class="text-body-2 mr-2">
            {{ $t("recipe.parser.select-parser") }}
          </div>
          <div class="d-flex align-center">
            <BaseOverflowButton
              v-model="parser"
              :disabled="state.loading.parser"
              btn-class="mx-2"
              :items="availableParsers"
            />
            <v-btn
              icon
              size="40"
              color="info"
              :disabled="state.loading.parser"
              @click="parseIngredients"
            >
              <v-icon>{{ $globals.icons.refresh }}</v-icon>
            </v-btn>
          </div>
        </div>
      </BaseCardSectionTitle>
      <AppLoader v-if="state.loading.parser" waiting-text="" class="my-6" />
      <v-card v-else-if="!state.allReviewed && currentIng">
        <v-card-text class="pb-0 mb-0">
          <div class="text-center px-8 py-4 mb-6">
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
          <v-card-actions>
            <v-spacer />
            <BaseButton
              v-if="currentMissingUnit && !currentIng.ingredient.unit?.id"
              color="warning"
              size="small"
              @click="createMissingUnit"
            >
              {{ i18n.t("recipe.parser.missing-unit", { unit: currentMissingUnit }) }}
            </BaseButton>
            <BaseButton
              v-if="currentMissingUnit && currentIng.ingredient.unit?.id"
              color="warning"
              size="small"
              @click="addMissingUnitAsAlias"
            >
              {{ i18n.t("recipe.parser.add-text-as-alias-for-item", { text: currentMissingUnit, item: currentIng.ingredient.unit.name }) }}
            </BaseButton>
            <BaseButton
              v-if="currentMissingFood && !currentIng.ingredient.food?.id"
              color="warning"
              size="small"
              @click="createMissingFood"
            >
              {{ i18n.t("recipe.parser.missing-food", { food: currentMissingFood }) }}
            </BaseButton>
            <BaseButton
              v-if="currentMissingFood && currentIng.ingredient.food?.id"
              color="warning"
              size="small"
              @click="addMissingFoodAsAlias"
            >
              {{ i18n.t("recipe.parser.add-text-as-alias-for-item", { text: currentMissingFood, item: currentIng.ingredient.food.name }) }}
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
                <div v-for="(ingredient, index) in parsedIngs" :key="index">
                  <RecipeIngredientEditor
                    v-model="ingredient.ingredient"
                    enable-context-menu
                    class="list-group-item"
                    @delete="parsedIngs.splice(index, 1)"
                    @insert-above="insertNewIngredient(index)"
                    @insert-below="insertNewIngredient(index + 1)"
                  />
                  <p class="pt-0 pb-4 my-0 text-caption">
                    {{ $t("recipe.original-text-with-value", { originalText: ingredient.input }) }}
                  </p>
                </div>
              </TransitionGroup>
            </VueDraggable>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
    <template v-if="!state.loading.parser" #custom-card-action>
      <BaseButton
        v-if="!state.allReviewed"
        color="info"
        :icon="$globals.icons.arrowRightBold"
        icon-right
        :text="$t('general.next')"
        @click="nextIngredient"
      />
      <BaseButton
        v-else
        create
        :text="$t('general.save')"
        :icon="$globals.icons.save"
        :loading="state.loading.save"
        @click="saveIngs"
      />
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import type { IngredientFood, IngredientUnit, ParsedIngredient, RecipeIngredient } from "~/lib/api/types/recipe";
import type { Parser } from "~/lib/api/user/recipes/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useAppInfo, useUserApi } from "~/composables/api";
import { parseIngredientText } from "~/composables/recipes";
import { useFoodData, useFoodStore, useUnitData, useUnitStore } from "~/composables/store";
import { useGlobalI18n } from "~/composables/use-global-i18n";
import { alert } from "~/composables/use-toast";
import { useParsingPreferences } from "~/composables/use-users/preferences";

const props = defineProps<{
  modelValue: boolean;
  ingredients: NoUndefinedField<RecipeIngredient[]>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "save", value: NoUndefinedField<RecipeIngredient[]>): void;
}>();

const i18n = useGlobalI18n();
const api = useUserApi();
const appInfo = useAppInfo();
const drag = ref(false);

const unitStore = useUnitStore();
const unitData = useUnitData();
const foodStore = useFoodStore();
const foodData = useFoodData();

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

const currentIng = ref<ParsedIngredient | null>(null);
const currentMissingUnit = ref("");
const currentMissingFood = ref("");
const currentIngHasError = computed(() => currentMissingUnit.value || currentMissingFood.value);

const state = reactive({
  currentParsedIndex: -1,
  allReviewed: false,
  loading: {
    parser: false,
    save: false,
  },
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
  const unit = ing.ingredient.unit?.name;
  if (!unit || ing.ingredient.unit?.id) {
    currentMissingUnit.value = "";
    return;
  }

  const potentialMatch = createdUnits.get(unit.toLowerCase());
  if (potentialMatch) {
    ing.ingredient.unit = potentialMatch;
    currentMissingUnit.value = "";
    return;
  }

  currentMissingUnit.value = unit;
  ing.ingredient.unit = undefined;
}

function checkFood(ing: ParsedIngredient) {
  const food = ing.ingredient.food?.name;
  if (!food || ing.ingredient.food?.id) {
    currentMissingFood.value = "";
    return;
  }

  const potentialMatch = createdFoods.get(food.toLowerCase());
  if (potentialMatch) {
    ing.ingredient.food = potentialMatch;
    currentMissingFood.value = "";
    return;
  }

  currentMissingFood.value = food;
  ing.ingredient.food = undefined;
}

function nextIngredient() {
  let nextIndex = state.currentParsedIndex + 1;

  while (nextIndex < parsedIngs.value.length) {
    const current = parsedIngs.value[nextIndex];
    if (shouldReview(current)) {
      state.currentParsedIndex = nextIndex;
      currentIng.value = current;
      checkUnit(current);
      checkFood(current);
      return;
    }

    nextIndex += 1;
  }

  // No more to review
  state.allReviewed = true;
}

async function parseIngredients() {
  if (state.loading.parser) {
    return;
  }

  if (!props.ingredients || props.ingredients.length === 0) {
    state.loading.parser = false;
    return;
  }
  state.loading.parser = true;
  try {
    const ingsAsString = props.ingredients.map(ing => parseIngredientText(ing, 1, false) ?? "");
    const { data, error } = await api.recipes.parseIngredients(parser.value, ingsAsString);
    if (error || !data) {
      throw new Error("Failed to parse ingredients");
    }
    parsedIngs.value = data;
    state.currentParsedIndex = -1;
    state.allReviewed = false;
    createdUnits.clear();
    createdFoods.clear();
    nextIngredient();
  }
  catch (error) {
    console.error("Error parsing ingredients:", error);
    alert.error(i18n.t("events.something-went-wrong"));
  }
  finally {
    state.loading.parser = false;
  }
}

/** Cache of lowercased created units to avoid duplicate creations */
const createdUnits = new Map<string, IngredientUnit>();
/** Cache of lowercased created foods to avoid duplicate creations */
const createdFoods = new Map<string, IngredientFood>();

async function createMissingUnit() {
  if (!currentMissingUnit.value) {
    return;
  }

  unitData.reset();
  unitData.data.name = currentMissingUnit.value;

  let newUnit: IngredientUnit | null = null;
  if (createdUnits.has(unitData.data.name)) {
    newUnit = createdUnits.get(unitData.data.name)!;
  }
  else {
    newUnit = await unitStore.actions.createOne(unitData.data);
  }

  if (!newUnit) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  currentIng.value!.ingredient.unit = newUnit;
  createdUnits.set(newUnit.name.toLowerCase(), newUnit);
  currentMissingUnit.value = "";
}

async function createMissingFood() {
  if (!currentMissingFood.value) {
    return;
  }

  foodData.reset();
  foodData.data.name = currentMissingFood.value;

  let newFood: IngredientFood | null = null;
  if (createdFoods.has(foodData.data.name)) {
    newFood = createdFoods.get(foodData.data.name)!;
  }
  else {
    newFood = await foodStore.actions.createOne(foodData.data);
  }

  if (!newFood) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  currentIng.value!.ingredient.food = newFood;
  createdFoods.set(newFood.name.toLowerCase(), newFood);
  currentMissingFood.value = "";
}

async function addMissingUnitAsAlias() {
  const unit = currentIng.value?.ingredient.unit as IngredientUnit | undefined;
  if (!currentMissingUnit.value || !unit?.id) {
    return;
  }

  unit.aliases = unit.aliases || [];
  if (unit.aliases.map(a => a.name).includes(currentMissingUnit.value)) {
    return;
  }

  unit.aliases.push({ name: currentMissingUnit.value });
  const updated = await unitStore.actions.updateOne(unit);
  if (!updated) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  currentIng.value!.ingredient.unit = updated;
  currentMissingUnit.value = "";
}

async function addMissingFoodAsAlias() {
  const food = currentIng.value?.ingredient.food as IngredientFood | undefined;
  if (!currentMissingFood.value || !food?.id) {
    return;
  }

  food.aliases = food.aliases || [];
  if (food.aliases.map(a => a.name).includes(currentMissingFood.value)) {
    return;
  }

  food.aliases.push({ name: currentMissingFood.value });
  const updated = await foodStore.actions.updateOne(food);
  if (!updated) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  currentIng.value!.ingredient.food = updated;
  currentMissingFood.value = "";
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

function saveIngs() {
  emit("save", parsedIngs.value.map(x => x.ingredient as NoUndefinedField<RecipeIngredient>));
  state.loading.save = true;
}
</script>
