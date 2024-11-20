<template>
  <div :class="dense ? 'wrapper' : 'wrapper pa-3'">
    <section>
      <v-container class="ma-0 pa-0">
        <v-row>
          <v-col
            v-if="preferences.imagePosition && preferences.imagePosition != ImagePosition.hidden"
            :order="preferences.imagePosition == ImagePosition.left ? -1 : 1"
            cols="4"
            align-self="center"
          >
            <img :key="imageKey" :src="recipeImageUrl" style="min-height: 50; max-width: 100%;" />
          </v-col>
          <v-col order=0>
            <v-card-title class="headline pl-0">
              <v-icon left color="primary">
                {{ $globals.icons.primary }}
              </v-icon>
              {{ recipe.name }}
            </v-card-title>
            <div v-if="recipeYield" class="d-flex justify-space-between align-center px-4 pb-2">
              <v-chip
                :small="$vuetify.breakpoint.smAndDown"
                label
              >
                <v-icon left>
                  {{ $globals.icons.potSteam }}
                </v-icon>
                <!-- eslint-disable-next-line vue/no-v-html -->
                <span v-html="recipeYield"></span>
              </v-chip>
            </div>
            <RecipeTimeCard
              :prep-time="recipe.prepTime"
              :total-time="recipe.totalTime"
              :perform-time="recipe.performTime"
              color="white"
            />
            <v-card-text v-if="preferences.showDescription" class="px-0">
              <SafeMarkdown :source="recipe.description" />
            </v-card-text>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Ingredients -->
    <section>
      <v-card-title class="headline pl-0"> {{ $t("recipe.ingredients") }} </v-card-title>
      <div
        v-for="(ingredientSection, sectionIndex) in ingredientSections"
        :key="`ingredient-section-${sectionIndex}`"
        class="print-section"
      >
        <h4 v-if="ingredientSection.ingredients[0].title" class="ingredient-title mt-2">
          {{ ingredientSection.ingredients[0].title }}
        </h4>
        <div
          class="ingredient-grid"
          :style="{ gridTemplateRows: `repeat(${Math.ceil(ingredientSection.ingredients.length / 2)}, min-content)` }"
        >
          <template v-for="(ingredient, ingredientIndex) in ingredientSection.ingredients">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <p :key="`ingredient-${ingredientIndex}`" class="ingredient-body" v-html="parseText(ingredient)" />
          </template>
        </div>
      </div>
    </section>

    <!-- Instructions -->
    <section>
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
            <h5>{{ step.summary ? step.summary : $t("recipe.step-index", { step: stepIndex + instructionSection.stepOffset + 1 }) }}</h5>
            <SafeMarkdown :source="step.text" class="recipe-step-body" />
          </div>
        </div>
      </div>
    </section>

    <!-- Notes -->
    <div v-if="preferences.showNotes">
      <v-divider v-if="hasNotes" class="grey my-4"></v-divider>

      <section>
        <div v-for="(note, index) in recipe.notes" :key="index + 'note'">
          <div class="print-section">
            <h4>{{ note.title }}</h4>
            <SafeMarkdown :source="note.text" class="note-body" />
          </div>
        </div>
      </section>
    </div>

    <!-- Nutrition -->
    <div v-if="preferences.showNutrition">
      <v-card-title class="headline pl-0"> {{ $t("recipe.nutrition") }} </v-card-title>

      <section>
        <div class="print-section">
          <table class="nutrition-table">
            <tbody>
              <tr v-for="(value, key) in recipe.nutrition" :key="key">
                <template v-if="value">
                  <td>{{ labels[key].label }}</td>
                  <td>{{ value ? (labels[key].suffix ? `${value} ${labels[key].suffix}` : value) : '-' }}</td>
                </template>
              </tr>
            </tbody>
          </table>
      </div>
    </section>
    </div>

  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import DOMPurify from "dompurify";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import { useStaticRoutes } from "~/composables/api";
import { Recipe, RecipeIngredient, RecipeStep} from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { ImagePosition, useUserPrintPreferences } from "~/composables/use-users/preferences";
import { parseIngredientText, useNutritionLabels } from "~/composables/recipes";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { useScaledAmount } from "~/composables/recipes/use-scaled-amount";


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
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    scale: {
      type: Number,
      default: 1,
    },
    dense: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const { i18n } = useContext();
    const preferences = useUserPrintPreferences();
    const { recipeImage } = useStaticRoutes();
    const { imageKey } = usePageState(props.recipe.slug);
    const {labels} = useNutritionLabels();

    function sanitizeHTML(rawHtml: string) {
      return DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
        ALLOWED_TAGS: ["strong", "sup"],
      });
    }

    const servingsDisplay = computed(() => {
      const { scaledAmountDisplay } = useScaledAmount(props.recipe.recipeYieldQuantity, props.scale);
      return scaledAmountDisplay ? i18n.t("recipe.yields-amount-with-text", {
        amount: scaledAmountDisplay,
        text: props.recipe.recipeYield,
      }) as string : "";
    })

    const yieldDisplay = computed(() => {
      const { scaledAmountDisplay } = useScaledAmount(props.recipe.recipeServings, props.scale);
      return scaledAmountDisplay ? i18n.t("recipe.serves-amount", { amount: scaledAmountDisplay }) as string : "";
    });

    const recipeYield = computed(() => {
      if (servingsDisplay.value && yieldDisplay.value) {
        return sanitizeHTML(`${yieldDisplay.value}; ${servingsDisplay.value}`);
      } else {
        return sanitizeHTML(yieldDisplay.value || servingsDisplay.value);
      }
    })

    const recipeImageUrl = computed(() => {
      return recipeImage(props.recipe.id, props.recipe.image, imageKey.value);
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
      return parseIngredientText(ingredient, props.recipe.settings?.disableAmount || false, props.scale);
    }

    return {
      labels,
      hasNotes,
      imageKey,
      ImagePosition,
      parseText,
      parseIngredientText,
      preferences,
      recipeImageUrl,
      recipeYield,
      ingredientSections,
      instructionSections,
    };
  },
});
</script>

<style scoped>
/* Makes all text solid black */
.wrapper {
  background-color: white;
}

.wrapper,
.wrapper >>> * {
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

.nutrition-table {
  max-width: 80%;
  border-collapse: collapse;
}

.nutrition-table th,
.nutrition-table td {
  padding: 6px 10px;
  text-align: left;
  vertical-align: top;
  font-size: 14px;
}

.nutrition-table th {
  font-weight: bold;
  padding-bottom: 10px;
}

.nutrition-table td:first-child {
  width: 70%;
  font-weight: bold;
}

.nutrition-table td:last-child {
  width: 30%;
  text-align: right;
}
.nutrition-table td {
  padding: 2px;
  text-align: left;
  font-size: 14px;
}

</style>
