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

    <section>
      <v-card-title class="headline pl-0"> {{ $t("recipe.ingredients") }} </v-card-title>
      <div class="ingredient-grid">
        <div class="ingredient-col-1">
          <ul>
            <li v-for="(text, index) in splitIngredients.firstHalf" :key="index">
              {{ text }}
            </li>
          </ul>
        </div>
        <div class="ingredient-col-2">
          <ul>
            <li v-for="(text, index) in splitIngredients.secondHalf" :key="index">
              {{ text }}
            </li>
          </ul>
        </div>
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
import { parseIngredientText } from "~/composables/recipes";

type SplitIngredients = {
  firstHalf: string[];
  secondHalf: string[];
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
    const splitIngredients = computed<SplitIngredients>(() => {
      const firstHalf = props.recipe.recipeIngredient
        ?.slice(0, Math.ceil(props.recipe.recipeIngredient.length / 2))
        .map((ingredient) => {
          return parseIngredientText(ingredient, props.recipe?.settings?.disableAmount || false);
        });

      const secondHalf = props.recipe.recipeIngredient
        ?.slice(Math.ceil(props.recipe.recipeIngredient.length / 2))
        .map((ingredient) => {
          return parseIngredientText(ingredient, props.recipe?.settings?.disableAmount || false);
        });

      return {
        firstHalf: firstHalf || [],
        secondHalf: secondHalf || [],
      };
    });

    const hasNotes = computed(() => {
      return props.recipe.notes && props.recipe.notes.length > 0;
    });

    return {
      hasNotes,
      splitIngredients,
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
