<template>
  <v-container
    v-if="recipe"
    :class="{
      'pa-0': $vuetify.breakpoint.smAndDown,
    }"
  >
    <v-card-title>
      <h1 class="headline">{{ recipe.name }}</h1>
    </v-card-title>

    <v-stepper v-model="activeStep" flat>
      <v-toolbar class="ma-1 elevation-2 rounded">
        <v-toolbar-title class="headline">
          Step {{ activeStep }} of {{ recipe.recipeInstructions.length }}</v-toolbar-title
        >
      </v-toolbar>
      <div class="d-flex mt-3 px-2">
        <BaseButton color="primary" @click="$router.go(-1)">
          <template #icon> {{ $globals.icons.arrowLeftBold }}</template>
          To Recipe
        </BaseButton>
        <v-btn rounded icon color="primary" class="ml-auto" small @click="scale > 1 ? scale-- : null">
          <v-icon>
            {{ $globals.icons.minus }}
          </v-icon>
        </v-btn>
        <v-btn rounded color="primary" small> Scale: {{ scale }} </v-btn>
        <v-btn rounded icon color="primary" small @click="scale++">
          <v-icon>
            {{ $globals.icons.createAlt }}
          </v-icon>
        </v-btn>
      </div>
      <v-stepper-items>
        <template v-for="(step, index) in recipe.recipeInstructions">
          <v-stepper-content :key="index + 1 + '-content'" :step="index + 1" class="pa-0 mt-2 elevation-0">
            <v-card class="ma-2">
              <v-card-text>
                <h2 class="mb-4">{{ $t("recipe.instructions") }}</h2>
                <VueMarkdown :source="step.text"> </VueMarkdown>
                <template v-if="step.ingredientReferences.length > 0">
                  <v-divider></v-divider>
                  <div>
                    <h2 class="mb-4 mt-4">{{ $t("recipe.ingredients") }}</h2>
                    <div
                      v-for="ing in step.ingredientReferences"
                      :key="ing.referenceId"
                      v-html="getIngredientByRefId(ing.referenceId)"
                    ></div>
                  </div>
                </template>
              </v-card-text>
            </v-card>
            <v-card-actions class="justify-center">
              <BaseButton color="primary" :disabled="index == 0" @click="activeStep = activeStep - 1">
                <template #icon> {{ $globals.icons.arrowLeftBold }}</template>
                Back
              </BaseButton>

              <BaseButton
                icon-right
                :disabled="index + 1 == recipe.recipeInstructions.length"
                color="primary"
                @click="activeStep = activeStep + 1"
              >
                <template #icon> {{ $globals.icons.arrowRightBold }}</template>
                Next
              </BaseButton>
            </v-card-actions>
          </v-stepper-content>
        </template>
      </v-stepper-items>
    </v-stepper>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useRoute, ref } from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import { useStaticRoutes } from "~/composables/api";
import { parseIngredientText, useRecipe } from "~/composables/recipes";

export default defineComponent({
  components: { VueMarkdown },
  setup() {
    const route = useRoute();
    const slug = route.value.params.slug;
    const activeStep = ref(1);
    const scale = ref(1);

    const { recipe } = useRecipe(slug);

    const { recipeImage } = useStaticRoutes();

    function getIngredientByRefId(refId: string) {
      if (!recipe.value) {
        return;
      }

      const ing = recipe?.value.recipeIngredient?.find((ing) => ing.referenceId === refId) || "";
      if (ing === "") {
        return "";
      }

      return parseIngredientText(ing, recipe?.value?.settings?.disableAmount || false, scale.value);
    }

    return {
      scale,
      getIngredientByRefId,
      activeStep,
      slug,
      recipe,
      recipeImage,
    };
  },
});
</script>
