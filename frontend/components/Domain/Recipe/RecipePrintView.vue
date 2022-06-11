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
      <div class="ingredient-grid">
        <template v-for="(ingredient, index) in recipe.recipeIngredient">
          <h4 v-if="ingredient.title" :key="`title-${index}`" class="ingredient-title mt-2">{{ ingredient.title }}</h4>
          <p :key="`ingredient-${index}`" v-html="parseText(ingredient)" />
        </template>
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
import { Recipe, RecipeIngredient } from "~/types/api-types/recipe";
import { parseIngredientText } from "~/composables/recipes";

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
.print-container,
.print-container >>> * {
  opacity: 1 !important;
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
  grid-gap: 0.5rem;
}

.ingredient-title {
  grid-column: 1 / span 2;
}

ul {
  padding-left: 1rem;
}

li {
  list-style-type: none;
  margin-bottom: 0.25rem;
}
</style>
