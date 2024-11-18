<template>
  <div>
    <v-text-field
      v-model="recipe.name"
      class="my-3"
      :label="$t('recipe.recipe-name')"
      :rules="[validators.required]"
    />
    <v-container class="ma-0 pa-0">
      <v-row>
        <v-col cols="3">
          <v-text-field
            v-model="recipeServings"
            type="number"
            :min="0"
            hide-spin-buttons
            dense
            :label="$t('recipe.servings')"
            @input="validateInput($event, 'recipeServings')"
          />
        </v-col>
        <v-col cols="3">
          <v-text-field
            v-model="recipeYieldQuantity"
            type="number"
            :min="0"
            hide-spin-buttons
            dense
            :label="$t('recipe.yield')"
            @input="validateInput($event, 'recipeYieldQuantity')"
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
          v-model="recipe.recipeYield"
          dense
          :label="$t('recipe.yield-text')"
        />
        </v-col>
      </v-row>
    </v-container>

    <div class="d-flex flex-wrap" style="gap: 1rem">
      <v-text-field v-model="recipe.totalTime" :label="$t('recipe.total-time')" />
      <v-text-field v-model="recipe.prepTime" :label="$t('recipe.prep-time')" />
      <v-text-field v-model="recipe.performTime" :label="$t('recipe.perform-time')" />
    </div>
    <v-textarea v-model="recipe.description" auto-grow min-height="100" :label="$t('recipe.description')" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { validators } from "~/composables/use-validators";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const recipeServings = computed<number>({
      get() {
        return props.recipe.recipeServings;
      },
      set(val) {
        validateInput(val.toString(), "recipeServings");
      },
    });

    const recipeYieldQuantity = computed<number>({
      get() {
        return props.recipe.recipeYieldQuantity;
      },
      set(val) {
        validateInput(val.toString(), "recipeYieldQuantity");
      },
    });

    function validateInput(value: string | null, property: "recipeServings" | "recipeYieldQuantity") {
      if (!value) {
        props.recipe[property] = 0;
        return;
      }

      const number = parseFloat(value.replace(/[^0-9.]/g, ""));
      if (isNaN(number) || number <= 0) {
        props.recipe[property] = 0;
        return;
      }

      props.recipe[property] = number;
    }

    return {
      validators,
      recipeServings,
      recipeYieldQuantity,
      validateInput,
    };
  },
});
</script>
