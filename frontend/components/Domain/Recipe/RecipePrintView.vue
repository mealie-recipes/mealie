<template>
  <div class="print-container">
    <section>
      <v-card-title class="headline pl-0">
        <v-icon left color="primary">
          {{ $globals.icons.primary }}
        </v-icon>
        {{ recipe.name }}
      </v-card-title>
      <RecipeTimeCard :prep-time="recipe.prepTime" :total-time="recipe.totalTime" :perform-time="recipe.performTime" />
    </section>

    <v-card-text class="px-0">
      <VueMarkdown :source="recipe.description" />
    </v-card-text>

    <!-- Ingredients -->
    <section>
      <v-card-title class="headline pl-0"> {{ $t("recipe.ingredients") }} </v-card-title>
      <div v-for="(ingredientSection, sectionIndex) in ingredientSections" :key="`ingredient-section-${sectionIndex}`" class="print-section">
        <div class="ingredient-grid">
          <template v-for="(ingredient, ingredientIndex) in ingredientSection.ingredients">
            <h4 v-if="ingredient.title" :key="`ingredient-title-${ingredientIndex}`" class="ingredient-title mt-2">{{ ingredient.title }}</h4>
            <p :key="`ingredient-${ingredientIndex}`" v-html="parseText(ingredient)" class="ingredient-body" />
          </template>
        </div>
      </div>
    </section>

    <!-- Instructions -->
    <section>
      <v-card-title class="headline pl-0">{{ $t("recipe.instructions") }}</v-card-title>
      <div v-for="(instructionSection, sectionIndex) in instructionSections" :key="`instruction-section-${sectionIndex}`" :class="{ 'print-section': instructionSection.sectionName }">
        <div v-for="(step, stepIndex) in instructionSection.instructions" :key="`instruction-${stepIndex}`">
          <div class="print-section">
            <h4 v-if="step.title" :key="`instruction-title-${stepIndex}`" class="instruction-title mb-2">{{ step.title }}</h4>
            <h5>{{ $t("recipe.step-index", { step: stepIndex + instructionSection.stepOffset + 1 }) }}</h5>
            <VueMarkdown :source="step.text" class="recipe-step-body" />
          </div>
        </div>
      </div>
    </section>

    <!-- Notes -->
    <v-divider v-if="hasNotes" class="grey my-4"></v-divider>

    <section>
      <div v-for="(note, index) in recipe.notes" :key="index + 'note'">
        <div class="print-section">
          <h4>{{ note.title }}</h4>
          <VueMarkdown :source="note.text" class="note-body" />
        </div>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";
// @ts-ignore vue-markdown has no types
import VueMarkdown from "@adapttive/vue-markdown";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import { Recipe, RecipeIngredient, RecipeStep } from "~/types/api-types/recipe";
import { parseIngredientText } from "~/composables/recipes";

type IngredientSection = {
  sectionName: string;
  ingredients: RecipeIngredient[];
};

type InstructionSection = {
  sectionName: string;
  stepOffset: number;
  instructions: RecipeStep[];
};

export default defineComponent({
  components: {
    RecipeTimeCard,
    VueMarkdown,
  },
  props: {
    recipe: {
      type: Object as () => Recipe,
      required: true,
    },
  },
  setup(props) {

    // Group ingredients by section so we can style them independently
    const ingredientSections = computed<IngredientSection[]>(() => {
      const ingredientSections:IngredientSection[] = [];
      const sectionIndexes:number[] = [];

      // Store indexes of each new section
      for (let i = 0; i < props.recipe.recipeIngredient.length; i++) {
        if (props.recipe.recipeIngredient[i].title) {
          sectionIndexes.push(i);
        }
      }
      sectionIndexes.push(props.recipe.recipeIngredient.length);

      // Make sure the first element is 0, otherwise we lose the first section of ingredients
      if (sectionIndexes[0] !== 0) {
        sectionIndexes.unshift(0);
      }

      // Create sections by slicing between section indexes
      for (let i = 0; i < sectionIndexes.length - 1; i++) {
        const startIndex:number = sectionIndexes[i];
        const endIndex:number = sectionIndexes[i + 1];
        const ingredientSection:IngredientSection = {
          sectionName: props.recipe.recipeIngredient[startIndex].title,
          ingredients: props.recipe.recipeIngredient.slice(startIndex, endIndex)
        };
        ingredientSections.push(ingredientSection);
      }

      return ingredientSections;
    });

    // Group instructions by section so we can style them independently
    const instructionSections = computed<InstructionSection[]>(() => {
      const instructionSections:InstructionSection[] = [];
      const sectionIndexes:number[] = [];

      // Store indexes of each new section
      for (let i = 0; i < props.recipe.recipeInstructions.length; i++) {
        if (props.recipe.recipeInstructions[i].title) {
          sectionIndexes.push(i);
        }
      }
      sectionIndexes.push(props.recipe.recipeInstructions.length);

      // Make sure the first element is 0, otherwise we lose the first section of instructions
      if (sectionIndexes[0] !== 0) {
        sectionIndexes.unshift(0);
      }

      // Create sections by slicing between section indexes
      for (let i = 0; i < sectionIndexes.length - 1; i++) {
        const startIndex:number = sectionIndexes[i];
        const endIndex:number = sectionIndexes[i + 1];
        const instructionSection:InstructionSection = {
          sectionName: props.recipe.recipeInstructions[startIndex].title,
          stepOffset: startIndex,
          instructions: props.recipe.recipeInstructions.slice(startIndex, endIndex)
        };
        instructionSections.push(instructionSection);
      }

      return instructionSections;
    });

    const hasNotes = computed(() => {
      return props.recipe.notes && props.recipe.notes.length > 0;
    });

    function parseText(ingredient: RecipeIngredient) {
      return parseIngredientText(ingredient, props.recipe.settings?.disableAmount || false);
    }

    return {
      hasNotes,
      parseText,
      parseIngredientText,
      ingredientSections,
      instructionSections,
    };
  },
});
</script>

<style>
@media print {
  body,
  html {
    margin-top: 0 !important;
  }

  .print-container {
    display: block !important;
  }

  .v-main {
    display: block;
  }

  .v-main__wrap {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>

<style scoped>
/* Makes all text solid black */
.print-container {
  display: none;
  background-color: white;
}

.print-container,
.print-container >>> * {
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

.v-card__text {
  padding-bottom: 0;
  margin-bottom: 0;
}

.ingredient-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 0.5rem;
}

.ingredient-title,
.instruction-title {
  grid-column: 1 / span 2;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.ingredient-body, .recipe-step-body, .note-body {
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
