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

      <div v-for="(ingredientSection, sectionIndex) in ingredientSections" :key="sectionIndex">

        <h4 v-if="ingredientSection.sectionName" class="mb-2">{{ ingredientSection.sectionName }}</h4>
        <div class="ingredient-grid">

          <!-- First Half of Ingredients -->
          <div class="ingredient-col-1">
            <ul>
              <div v-for="(ingredientText, ingredientIndex) in ingredientSection.firstHalf" :key="ingredientIndex">
                <li v-html="ingredientText" />
              </div>
            </ul>
          </div>

          <!-- Second Half of Ingredients -->
          <div class="ingredient-col-2">
            <ul>
              <div v-for="(ingredientText, ingredientIndex) in ingredientSection.secondHalf" :key="ingredientIndex">
                <li v-html="ingredientText" />
              </div>
            </ul>
          </div>

        </div>

        <br v-if="sectionIndex != ingredientSections.length - 1" />

      </div>
    </section>

    <section>
      <v-card-title class="headline pl-0">{{ $t("recipe.instructions") }}</v-card-title>
      <div v-for="(step, index) in recipe.recipeInstructions" :key="index">
        <h3 v-if="step.title" class="mb-2">{{ step.title }}</h3>
        <div class="ml-5">
          <h4>{{ $t("recipe.step-index", { step: index + 1 }) }}</h4>
          <VueMarkdown :source="step.text" />
        </div>
      </div>
    </section>

    <v-divider v-if="hasNotes" class="grey my-4"></v-divider>

    <section>
      <div v-for="(note, index) in recipe.notes" :key="index + 'note'">
        <h4>{{ note.title }}</h4>
        <VueMarkdown :source="note.text" />
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";
// @ts-ignore vue-markdown has no types
import VueMarkdown from "@adapttive/vue-markdown";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import { Recipe } from "~/types/api-types/recipe";
import { RecipeIngredient } from "~/types/api-types/recipe";
import { parseIngredientText } from "~/composables/recipes";

type IngredientSection = {
  sectionName: string;
  ingredients: RecipeIngredient[];
  firstHalf: string[];
  secondHalf: string[];
}

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
    const ingredientSections = computed<IngredientSection[]>(() => {
      let ingredientSections:IngredientSection[] = [];
      let sectionIndexes:number[] = [];

      // Store indexes of each new section
      for (let i = 0; i < props.recipe.recipeIngredient.length; i++) {
        if (props.recipe.recipeIngredient[i].title) {
          sectionIndexes.push(i);
        }
      }
      sectionIndexes.push(props.recipe.recipeIngredient.length);

      // Make sure the first element is 0
      if (sectionIndexes[0] !== 0) {
        sectionIndexes.unshift(0);
      }

      // Create sections by slicing between section indexes
      for (let i = 0; i < sectionIndexes.length - 1; i++) {
        const startIndex:number = sectionIndexes[i];
        const endIndex:number = sectionIndexes[i + 1];

        let ingredientSection:IngredientSection = {
          sectionName: props.recipe.recipeIngredient[startIndex].title,
          ingredients: props.recipe.recipeIngredient.slice(startIndex, endIndex)
        };

        ingredientSections.push(ingredientSection);
      }

      // Split each section's ingredients in half
      for (let i = 0; i < ingredientSections.length; i++) {
        ingredientSections[i].firstHalf = ingredientSections[i].ingredients
          ?.slice(0, Math.ceil(ingredientSections[i].ingredients.length / 2))
          .map((ingredient) => {
            return parseIngredientText(ingredient, props.recipe?.settings?.disableAmount || false);
          });

        ingredientSections[i].secondHalf = ingredientSections[i].ingredients
          ?.slice(Math.ceil(ingredientSections[i].ingredients.length / 2))
          .map((ingredient) => {
            return parseIngredientText(ingredient, props.recipe?.settings?.disableAmount || false);
          });
      }

      return ingredientSections;
    });

    const hasNotes = computed(() => {
      return props.recipe.notes && props.recipe.notes.length > 0;
    });

    return {
      hasNotes,
      ingredientSections,
      parseIngredientText,
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
.print-container {
  display: none;
  background-color: white;
}

/* Makes all text solid black */
.print-container, .print-container >>> * {
  opacity: 1.0 !important;
  color: black !important;
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
  grid-gap: 1rem;
}

ul {
  padding-left: 1rem;
}

li {
  list-style-type: none;
  margin-bottom: 0.25rem;
}
</style>
