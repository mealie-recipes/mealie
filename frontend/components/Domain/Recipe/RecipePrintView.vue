<template>
  <div class="print-container">
    <section class="recipe-header">
      <div class="recipe-header-image-left">
        <v-img
          v-if="recipePrintOptions.recipeImagePosition === RecipeImagePosition.Left"
          :src="recipeImage(recipe.id, recipe.image, recipeImageKey)"
          @error="hideImage = true"
        ></v-img>
      </div>

      <div
        class="recipe-header-content"
        :style="`width: ${
          recipePrintOptions.recipeImagePosition && recipePrintOptions.recipeImagePosition === RecipeImagePosition.Hidden
          ? '100%' : '50%'
        }`"
      >
        <v-card-title class="recipe-title headline pl-0">
          <v-icon left color="primary">
            {{ $globals.icons.primary }}
          </v-icon>
          {{ recipe.name }}
        </v-card-title>

        <div v-if="showTimeCards" class="recipe-timecard">
          <div v-for="(time, index) in allTimes" :key="`timecard-${index}`">
            <v-icon left>
              {{ $globals.icons.clockOutline }}
            </v-icon>
            {{ time.name }} | {{ time.value }}
          </div>
        </div>

        <v-card-text v-if="recipePrintOptions.displayDescription" class="px-0">
          <SafeMarkdown :source="recipe.description" />
        </v-card-text>
      </div>

      <div class="recipe-header-image-right">
        <v-img
          v-if="recipePrintOptions.recipeImagePosition === RecipeImagePosition.Right"
          :src="recipeImage(recipe.id, recipe.image, recipeImageKey)"
          @error="hideImage = true"
        ></v-img>
      </div>
    </section>

    <div style="clear:both;"></div>
    <v-divider class="grey my-4"></v-divider>

    <!-- Ingredients -->
    <section class="recipe-ingredients">
      <div
        v-for="(ingredientSection, sectionIndex) in ingredientSections"
        :key="`ingredient-section-${sectionIndex}`"
        class="print-section"
      >
        <v-card-title v-if="!sectionIndex" class="headline pl-0"> {{ $t("recipe.ingredients") }} </v-card-title>
        <h4 v-if="ingredientSection.ingredients[0].title" class="ingredient-title mt-2">
            {{ ingredientSection.ingredients[0].title }}
        </h4>
        <div class="ingredient-grid" :style="{gridTemplateRows:`repeat(${Math.ceil(ingredientSection.ingredients.length / 2)}, min-content)`}">
          <template v-for="(ingredient, ingredientIndex) in ingredientSection.ingredients">
            <p :key="`ingredient-${ingredientIndex}`" class="ingredient-body" v-html="parseText(ingredient)" />
          </template>
        </div>
      </div>
    </section>

    <div style="clear:both;"></div>

    <!-- Instructions -->
    <section class="recipe-instructions">
      <div
        v-for="(instructionSection, sectionIndex) in instructionSections"
        :key="`instruction-section-${sectionIndex}`"
        :class="{ 'print-section': instructionSection.sectionName }"
      >
        <v-card-title v-if="!sectionIndex" class="headline pl-0">{{ $t("recipe.instructions") }}</v-card-title>
        <div v-for="(step, stepIndex) in instructionSection.instructions" :key="`instruction-${stepIndex}`">
          <div class="print-section">
            <h4 v-if="step.title" :key="`instruction-title-${stepIndex}`" class="instruction-title mb-2">
              {{ step.title }}
            </h4>
            <h5>{{ $t("recipe.step-index", { step: stepIndex + instructionSection.stepOffset + 1 }) }}</h5>
            <SafeMarkdown :source="step.text" class="recipe-step-body" />
          </div>
        </div>
      </div>
    </section>

    <div style="clear:both;"></div>

    <!-- Notes -->
    <section v-if="recipePrintOptions.displayNotes && hasNotes" class="recipe-notes">
      <v-divider class="grey my-4"></v-divider>
      <div v-for="(note, index) in recipe.notes" :key="index + 'note'">
        <div class="print-section">
          <h4>{{ note.title }}</h4>
          <SafeMarkdown :source="note.text" class="note-body" />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, useContext } from "@nuxtjs/composition-api";
import { Recipe, RecipeIngredient, RecipeStep } from "~/types/api-types/recipe";
import { useStaticRoutes } from "~/composables/api";
import { parseIngredientText } from "~/composables/recipes";
import { icons } from "~/utils/icons/icons"

type IngredientSection = {
  sectionName: string;
  ingredients: RecipeIngredient[];
};

type InstructionSection = {
  sectionName: string;
  stepOffset: number;
  instructions: RecipeStep[];
};

export const RecipeImagePosition = {
  Hidden: {
    label: "Don't Display",
    value: "hidden",
    icon: icons.close,
  },
  Left: {
    label: "Left",
    value: "left",
    icon: icons.dockLeft,
  },
  Right: {
    label: "Right",
    value: "right",
    icon: icons.dockRight,
  },
}

export const RecipePrintOptions = {
  recipeImagePosition: RecipeImagePosition.Hidden,
  displayDescription: true,
  displayNotes: true,
}

export default defineComponent({
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
    recipeImageKey: {
      type: Number,
      default: 1,
    },
    recipePrintOptions: {
      type: Object as () => typeof RecipePrintOptions,
      required: true,
    },
  },
  setup(props) {
    const { i18n } = useContext();
    const { recipeImage } = useStaticRoutes();

    // Get an array of all timecard props
    function timecardIsEmpty(str: string | null | undefined) {
      return !str || str.length === 0;
    }

    const showTimeCards = computed(() => {
      return [props.recipe.prepTime, props.recipe.totalTime, props.recipe.performTime].some((x) => !timecardIsEmpty(x));
    });

    const validateTotalTime = computed(() => {
      return !timecardIsEmpty(props.recipe.totalTime) ? { name: i18n.t("recipe.total-time"), value: props.recipe.totalTime } : null;
    });

    const validatePrepTime = computed(() => {
      return !timecardIsEmpty(props.recipe.prepTime) ? { name: i18n.t("recipe.prep-time"), value: props.recipe.prepTime } : null;
    });

    const validatePerformTime = computed(() => {
      return !timecardIsEmpty(props.recipe.performTime) ? { name: i18n.t("recipe.perform-time"), value: props.recipe.performTime } : null;
    });

    const allTimes = computed(() => {
      return [validateTotalTime.value, validatePrepTime.value, validatePerformTime.value].filter((x) => x !== null);
    });

    // Group ingredients by section so we can style them independently
    const ingredientSections = computed<IngredientSection[]>(() => {
      if (!props.recipe.recipeIngredient) {
        return [];
      }

      return props.recipe.recipeIngredient.reduce((sections, ingredient) => {
        // if title append new section to the end of the array
        if (ingredient.title) {
          sections.push({
            sectionName: ingredient.title,
            ingredients: [ingredient],
          });

          return sections;
        }

        // append new section if first
        if (sections.length === 0) {
          sections.push({
            sectionName: "",
            ingredients: [ingredient],
          });

          return sections;
        }

        // otherwise add ingredient to last section in the array
        sections[sections.length - 1].ingredients.push(ingredient);
        return sections;
      }, [] as IngredientSection[]);
    });

    // Group instructions by section so we can style them independently
    const instructionSections = computed<InstructionSection[]>(() => {
      if (!props.recipe.recipeInstructions) {
        return [];
      }

      return props.recipe.recipeInstructions.reduce((sections, step) => {
        const offset = (() => {
          if (sections.length === 0) {
            return 0;
          }

          const lastOffset = sections[sections.length - 1].stepOffset;
          const lastNumSteps = sections[sections.length - 1].instructions.length;
          return lastOffset + lastNumSteps;
        })();

        // if title append new section to the end of the array
        if (step.title) {
          sections.push({
            sectionName: step.title,
            stepOffset: offset,
            instructions: [step],
          });

          return sections;
        }

        // append if first element
        if (sections.length === 0) {
          sections.push({
            sectionName: "",
            stepOffset: offset,
            instructions: [step],
          });

          return sections;
        }

        // otherwise add step to last section in the array
        sections[sections.length - 1].instructions.push(step);
        return sections;
      }, [] as InstructionSection[]);
    });

    const hasNotes = computed(() => {
      return props.recipe.notes && props.recipe.notes.length > 0;
    });

    function parseText(ingredient: RecipeIngredient) {
      return parseIngredientText(ingredient, props.recipe.settings?.disableAmount || false);
    }

    return {
      showTimeCards,
      allTimes,
      RecipeImagePosition,
      recipeImage,
      parseText,
      parseIngredientText,
      ingredientSections,
      instructionSections,
      hasNotes,
    };
  },
});
</script>

<style scoped>
.print-container {
  background-color: white;
  display: block;
  padding: 20px;
}

.print-container,
.print-container >>> * {
  /* Makes all text solid black*/
  opacity: 1 !important;
  color: black !important;
}

/* Prevents sections from being broken up between pages */
.print-section {
  page-break-inside: avoid;
}

p {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
}

.recipe-header {
  display: block;
  text-align: center;
}

.recipe-header > div {
  padding: 0px 10px 0px 10px;
  box-sizing: border-box;
}

.recipe-header-image-left,
.recipe-header-image-right {
  width: 50%;
  float: left;
}

.recipe-header-content {
  float: left;
}

.recipe-title,
.recipe-title > * {
  display: inline;
}

.recipe-timecard {
  text-align: center;
}

.recipe-timecard > div {
  margin: 10px;
  display: inline-block;
  text-align: left;
}

.recipe-header > div >>> * {
  text-align: left;
}

.ingredient-grid {
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: 1fr 1fr;
  grid-gap: 0.5rem;
}

.ingredient-title,
.instruction-title {
  grid-column: 1 / span 2;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.ingredient-body,
.recipe-step-body,
.note-body {
  font-size: 14px;
}

ul {
  padding-left: 1rem;
}

li {
  list-style-type: none;
  margin-bottom: 0.25rem;
}
</style>
