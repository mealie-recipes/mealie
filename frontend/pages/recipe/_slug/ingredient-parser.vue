<template>
  <v-container v-if="recipe">
    <v-container>
      <BaseCardSectionTitle title="Ingredients Processor">
        To use the ingredient parser, click the "Parse All" button and the process will start. When the processed
        ingredients are available, you can look through the items and verify that they were parsed correctly. The models
        confidence score is displayed on the right of the title item. This is an average of all scores and may not be
        wholey accurate.

        <div class="mt-6">
          Alerts will be displayed if a matching foods or unit is found but does not exists in the database.
        </div>
        <v-divider class="my-4"> </v-divider>
        <div class="mb-n4">
          Select Parser
          <BaseOverflowButton
            v-model="parser"
            btn-class="mx-2"
            :items="[
              {
                text: 'Natural Language Processor ',
                value: 'nlp',
              },
              {
                text: 'Brute Parser',
                value: 'brute',
              },
            ]"
          />
        </div>
      </BaseCardSectionTitle>

      <v-card-actions class="justify-end">
        <BaseButton color="info" @click="fetchParsed">
          <template #icon> {{ $globals.icons.foods }}</template>
          Parse All
        </BaseButton>
        <BaseButton save @click="saveAll"> Save All </BaseButton>
      </v-card-actions>

      <v-expansion-panels v-model="panels" multiple>
        <v-expansion-panel v-for="(ing, index) in parsedIng" :key="index">
          <v-expansion-panel-header class="my-0 py-0" disable-icon-rotate>
            {{ ing.input }}
            <template #actions>
              <v-icon left :color="isError(ing) ? 'error' : 'success'">
                {{ isError(ing) ? $globals.icons.alert : $globals.icons.check }}
              </v-icon>
              <div class="my-auto" :color="isError(ing) ? 'error-text' : 'success-text'">
                {{ asPercentage(ing.confidence.average) }}
              </div>
            </template>
          </v-expansion-panel-header>
          <v-expansion-panel-content class="pb-0 mb-0">
            <RecipeIngredientEditor v-model="parsedIng[index].ingredient" />
            <v-card-actions>
              <v-spacer></v-spacer>
              <BaseButton
                v-if="errors[index].foodError && errors[index].foodErrorMessage !== ''"
                color="warning"
                small
                @click="createFood(ing.ingredient.food, index)"
              >
                {{ errors[index].foodErrorMessage }}
              </BaseButton>
            </v-card-actions>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent, ref, useRoute, useRouter } from "@nuxtjs/composition-api";
import { Food, ParsedIngredient, Parser } from "~/api/class-interfaces/recipes";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import { useUserApi } from "~/composables/api";
import { useRecipe, useFoods, useUnits } from "~/composables/recipes";
import { RecipeIngredientUnit } from "~/types/api-types/recipe";

interface Error {
  ingredientIndex: number;
  unitError: Boolean;
  unitErrorMessage: string;
  foodError: Boolean;
  foodErrorMessage: string;
}

export default defineComponent({
  components: {
    RecipeIngredientEditor,
  },
  setup() {
    const panels = ref<number[]>([]);

    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useUserApi();

    const { recipe, loading } = useRecipe(slug);

    const ingredients = ref<any[]>([]);

    // =========================================================
    // Parser Logic

    const parser = ref<Parser>("nlp");

    const parsedIng = ref<any[]>([]);

    async function fetchParsed() {
      if (!recipe.value) {
        return;
      }
      const raw = recipe.value.recipeIngredient.map((ing) => ing.note);
      const { response, data } = await api.recipes.parseIngredients(parser.value, raw);
      console.log({ response });

      if (data) {
        parsedIng.value = data;

        console.log(data);

        // @ts-ignore
        errors.value = data.map((ing, index: number) => {
          const unitError = !checkForUnit(ing.ingredient.unit);
          const foodError = !checkForFood(ing.ingredient.food);

          let unitErrorMessage = "";
          let foodErrorMessage = "";

          if (unitError || foodError) {
            if (unitError) {
              if (ing?.ingredient?.unit?.name) {
                unitErrorMessage = `Create missing unit '${ing?.ingredient?.unit?.name || "No unit"}'`;
              }
            }

            if (foodError) {
              if (ing?.ingredient?.food?.name) {
                foodErrorMessage = `Create missing food '${ing.ingredient.food.name || "No food"}'?`;
              }
              panels.value.push(index);
            }
          }

          return {
            ingredientIndex: index,
            unitError,
            unitErrorMessage,
            foodError,
            foodErrorMessage,
          };
        });
      }
    }

    function isError(ing: ParsedIngredient) {
      if (!ing?.confidence?.average) {
        return true;
      }
      return !(ing.confidence.average >= 0.75);
    }

    function asPercentage(num: number) {
      return Math.round(num * 100).toFixed(2) + "%";
    }

    // =========================================================
    // Food and Ingredient Logic

    const { foods, workingFoodData, actions } = useFoods();
    const { units } = useUnits();

    const errors = ref<Error[]>([]);

    function checkForUnit(unit: RecipeIngredientUnit) {
      if (units.value && unit?.name) {
        return units.value.some((u) => u.name === unit.name);
      }
      return false;
    }

    function checkForFood(food: Food) {
      if (foods.value && food?.name) {
        return foods.value.some((f) => f.name === food.name);
      }
      return false;
    }

    async function createFood(food: Food, index: number) {
      workingFoodData.name = food.name;
      await actions.createOne();
      errors.value[index].foodError = false;
    }

    // =========================================================
    // Save All Loginc
    async function saveAll() {
      let ingredients = parsedIng.value.map((ing) => {
        return {
          ...ing.ingredient,
        };
      });

      console.log(ingredients);

      ingredients = ingredients.map((ing) => {
        if (!foods.value || !units.value) {
          return ing;
        }
        // Get food from foods
        const food = foods.value.find((f) => f.name === ing.food.name);
        ing.food = food || null;

        // Get unit from units
        const unit = units.value.find((u) => u.name === ing.unit.name);
        ing.unit = unit || null;
        console.log(ing);

        return ing;
      });

      if (!recipe.value) {
        return;
      }

      recipe.value.recipeIngredient = ingredients;
      const { response } = await api.recipes.updateOne(recipe.value.slug, recipe.value);

      if (response?.status === 200) {
        router.push("/recipe/" + recipe.value.slug);
      }
    }

    return {
      parser,
      saveAll,
      createFood,
      errors,
      actions,
      workingFoodData,
      isError,
      panels,
      asPercentage,
      fetchParsed,
      parsedIng,
      recipe,
      loading,
      ingredients,
    };
  },
  head() {
    return {
      title: "Parser",
    };
  },
});
</script>
  
