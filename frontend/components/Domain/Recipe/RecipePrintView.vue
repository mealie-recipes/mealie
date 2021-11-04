<template>
  <div>
    <div v-if="recipe" class="container print">
      <div>
        <h1>
          <svg class="icon" viewBox="0 0 24 24">
            <path
              fill="#E58325"
              d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
            />
          </svg>
          {{ recipe.name }}
        </h1>
      </div>
      <div class="time-container">
        <RecipeTimeCard
          :prep-time="recipe.prepTime"
          :total-time="recipe.totalTime"
          :perform-time="recipe.performTime"
        />
      </div>
      <v-btn
        v-if="recipe.recipeYield"
        dense
        small
        :hover="false"
        type="label"
        :ripple="false"
        elevation="0"
        color="secondary darken-1"
        class="rounded-sm static"
      >
        {{ recipe.recipeYield }}
      </v-btn>
      <div>
        <VueMarkdown :source="recipe.description"> </VueMarkdown>
        <h2>{{ $t("recipe.ingredients") }}</h2>
        <ul>
          <li v-for="(ingredient, index) in recipe.recipeIngredient" :key="index">
            <v-icon>
              {{ $globals.icons.checkboxBlankOutline }}
            </v-icon>
            <p>{{ ingredient.note }}</p>
          </li>
        </ul>
      </div>
      <div>
        <h2>{{ $t("recipe.instructions") }}</h2>
        <div v-for="(step, index) in recipe.recipeInstructions" :key="index">
          <h2 v-if="step.title">{{ step.title }}</h2>
          <div class="ml-5">
            <h3>{{ $t("recipe.step-index", { step: index + 1 }) }}</h3>
            <VueMarkdown :source="step.text"> </VueMarkdown>
          </div>
        </div>

        <br />
        <v-divider v-if="recipe.notes.length > 0" class="mb-5 mt-0"></v-divider>

        <div v-for="(note, index) in recipe.notes" :key="index + 'note'">
          <h3>{{ note.title }}</h3>
          <VueMarkdown :source="note.text"> </VueMarkdown>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import { Recipe } from "~/types/api-types/recipe";
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
});
</script>

<style>
@media print {
  body,
  html {
    margin-top: -40px !important;
  }
}

h1 {
  margin-top: 0 !important;
  display: -webkit-box;
  display: flex;
  font-size: 2rem;
  letter-spacing: -0.015625em;
  font-weight: 300;
  padding: 0;
}

h2 {
  margin-bottom: 0.25rem;
}

h3 {
  margin-bottom: 0.25rem;
}

ul {
  padding-left: 1rem;
}

li {
  display: -webkit-box;
  display: -webkit-flex;
  margin-left: 0;
  margin-bottom: 0.5rem;
}

li p {
  margin-left: 0.25rem;
  margin-bottom: 0 !important;
}

p {
  margin: 0;
  font-size: 1rem;
  letter-spacing: 0.03125em;
  font-weight: 400;
}

.icon {
  margin-top: auto;
  margin-bottom: auto;
  margin-right: 0.5rem;
  height: 3rem;
  width: 3rem;
}

.time-container {
  display: flex;
  justify-content: left;
}

.time-chip {
  border-radius: 0.25rem;
  border-color: black;
  border: 1px;
  border-top: 1px;
}

.print {
  display: none;
}

@media print {
  .print {
    display: initial;
  }
}
</style>