<template>
  <div>
    <div class="d-flex justify-end flex-wrap align-stretch">
      <RecipePageInfoCardImage v-if="landscape" :recipe="recipe" />
      <v-card
        :width="landscape ? '100%' : '50%'"
        flat
        class="d-flex flex-column justify-center align-center"
      >
        <v-card-text>
          <v-card-title class="headline pa-0 flex-column align-center">
            {{ recipe.name }}
            <RecipeRating :key="recipe.slug" :value="recipe.rating" :recipe-id="recipe.id" :slug="recipe.slug" />
          </v-card-title>
          <v-divider class="my-2" />
          <SafeMarkdown :source="recipe.description" />
          <v-divider />
          <v-container class="d-flex flex-row flex-wrap justify-center align-center">
            <div class="mx-5">
              <v-row no-gutters class="mb-1">
                <v-col v-if="recipe.recipeYieldQuantity || recipe.recipeYield" cols="12" class="d-flex flex-wrap justify-center">
                  <RecipeYield
                    :yield-quantity="recipe.recipeYieldQuantity"
                    :yield="recipe.recipeYield"
                    :scale="recipeScale"
                  />
                </v-col>
              </v-row>
              <v-row no-gutters>
                <v-col cols="12" class="d-flex flex-wrap justify-center">
                  <RecipeLastMade
                    v-if="isOwnGroup"
                    :recipe="recipe"
                    :class="true ? undefined : 'force-bottom'"
                  />
                </v-col>
              </v-row>
            </div>
            <div class="mx-5">
              <RecipeTimeCard
                stacked
                container-class="d-flex flex-wrap justify-center"
                :prep-time="recipe.prepTime"
                :total-time="recipe.totalTime"
                :perform-time="recipe.performTime"
              />
            </div>
          </v-container>
        </v-card-text>
      </v-card>
      <RecipePageInfoCardImage v-if="!landscape" :recipe="recipe" max-width="50%" class="my-auto" />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeLastMade from "~/components/Domain/Recipe/RecipeLastMade.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeYield from "~/components/Domain/Recipe/RecipeYield.vue";
import RecipePageInfoCardImage from "~/components/Domain/Recipe/RecipePage/RecipePageParts/RecipePageInfoCardImage.vue";
import { Recipe } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
export default defineComponent({
  components: {
    RecipeRating,
    RecipeLastMade,
    RecipeTimeCard,
    RecipeYield,
    RecipePageInfoCardImage,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    recipeScale: {
      type: Number,
      default: 1,
    },
    landscape: {
      type: Boolean,
      required: true,
    },
  },
  setup() {
    const { $vuetify } = useContext();
    const useMobile = computed(() => $vuetify.breakpoint.smAndDown);

    const { isOwnGroup } = useLoggedInState();

    return {
      isOwnGroup,
      useMobile,
    };
  }
});
</script>
