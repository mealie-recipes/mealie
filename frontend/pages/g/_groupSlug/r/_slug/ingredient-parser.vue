<template>
  <v-container v-if="recipe">
    <v-container>
      <v-alert dismissible border="left" colored-border type="warning" elevation="2" :icon="$globals.icons.alert">
        <b>Experimental Feature</b>
        <div>
          Mealie can use natural language processing to attempt to parse and create units, and foods for your Recipe
          ingredients. This is experimental and may not work as expected. If you choose to not use the parsed results
          you can select cancel and your changes will not be saved.
        </div>
      </v-alert>

      <BaseCardSectionTitle title="Ingredients Processor">
        To use the ingredient parser, click the "Parse All" button and the process will start. When the processed
        ingredients are available, you can look through the items and verify that they were parsed correctly. The models
        confidence score is displayed on the right of the title item. This is an average of all scores and may not be
        wholely accurate.

        <div class="my-4">
          Alerts will be displayed if a matching foods or unit is found but does not exists in the database.
        </div>
        <div class="d-flex align-center mb-n4">
          <div class="mb-4">Select Parser</div>
          <BaseOverflowButton
            v-model="parser"
            btn-class="mx-2 mb-4"
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

      <div class="d-flex mt-n3 mb-4 justify-end" style="gap: 5px">
        <BaseButton cancel class="mr-auto" @click="$router.go(-1)"></BaseButton>
        <BaseButton color="info" @click="fetchParsed">
          <template #icon> {{ $globals.icons.foods }}</template>
          Parse All
        </BaseButton>
        <BaseButton save @click="saveAll"> Save All </BaseButton>
      </div>

      <v-expansion-panels v-model="panels" multiple>
        <draggable
          v-if="parsedIng.length > 0"
          v-model="parsedIng"
          handle=".handle"
          :style="{ width: '100%' }"
          ghost-class="ghost"
        >
          <v-expansion-panel v-for="(ing, index) in parsedIng" :key="index">
            <v-expansion-panel-header class="my-0 py-0" disable-icon-rotate>
              <template #default="{ open }">
                <v-fade-transition>
                  <span v-if="!open" key="0"> {{ ing.input }} </span>
                </v-fade-transition>
              </template>
              <template #actions>
                <v-icon left :color="isError(ing) ? 'error' : 'success'">
                  {{ isError(ing) ? $globals.icons.alert : $globals.icons.check }}
                </v-icon>
                <div class="my-auto" :color="isError(ing) ? 'error-text' : 'success-text'">
                  {{ ing.confidence ? asPercentage(ing.confidence.average) : "" }}
                </div>
              </template>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="pb-0 mb-0">
              <RecipeIngredientEditor v-model="parsedIng[index].ingredient" allow-insert-ingredient @insert-ingredient="insertIngredient(index)"  @delete="deleteIngredient(index)" />
              {{ ing.input }}
              <v-card-actions>
                <v-spacer />
                <BaseButton
                  v-if="errors[index].unitError && errors[index].unitErrorMessage !== ''"
                  color="warning"
                  small
                  @click="createUnit(ing.ingredient.unit, index)"
                >
                  {{ errors[index].unitErrorMessage }}
                </BaseButton>
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
        </draggable>
      </v-expansion-panels>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, useRoute, useRouter } from "@nuxtjs/composition-api";
import { invoke, until } from "@vueuse/core";
import draggable from "vuedraggable";
import {
  CreateIngredientFood,
  CreateIngredientUnit,
  IngredientFood,
  IngredientUnit,
  ParsedIngredient,
  RecipeIngredient,
} from "~/lib/api/types/recipe";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import { useUserApi } from "~/composables/api";
import { useRecipe } from "~/composables/recipes";
import { useFoodData, useFoodStore, useUnitStore, useUnitData } from "~/composables/store";
import { Parser } from "~/lib/api/user/recipes/recipe";
import { uuid4 } from "~/composables/use-utils";

interface Error {
  ingredientIndex: number;
  unitError: boolean;
  unitErrorMessage: string;
  foodError: boolean;
  foodErrorMessage: string;
}

export default defineComponent({
  components: {
    RecipeIngredientEditor,
    draggable
  },
  setup() {
    const { $auth } = useContext();
    const panels = ref<number[]>([]);

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useUserApi();

    const { recipe, loading } = useRecipe(slug);

    invoke(async () => {
      await until(recipe).not.toBeNull();

      fetchParsed();
    });

    const ingredients = ref<any[]>([]);

    // =========================================================
    // Parser Logic
    const parser = ref<Parser>("nlp");
    const parsedIng = ref<ParsedIngredient[]>([]);

    function processIngredientError(ing: ParsedIngredient, index: number): Error {
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
        }
      }
      panels.value.push(index);

      return {
        ingredientIndex: index,
        unitError,
        unitErrorMessage,
        foodError,
        foodErrorMessage,
      } as Error;
    }

    async function fetchParsed() {
      if (!recipe.value || !recipe.value.recipeIngredient) {
        return;
      }
      const raw = recipe.value.recipeIngredient.map((ing) => ing.note ?? "");
      const { data } = await api.recipes.parseIngredients(parser.value, raw);

      if (data) {
        // When we send the recipe ingredient text to be parsed, we lose the reference to the original unparsed ingredient.
        // Generally this is fine, but if the unparsed ingredient had a title, we lose it; we add back the title for each ingredient here.
        try {
          for (let i = 0; i < recipe.value.recipeIngredient.length; i++) {
            data[i].ingredient.title = recipe.value.recipeIngredient[i].title;
          }
        } catch (TypeError) {
          console.error("Index Mismatch Error during recipe ingredient parsing; did the number of ingredients change?");
        }

        parsedIng.value = data;

        errors.value = data.map((ing, index: number) => {
          return processIngredientError(ing, index);
        });
      }
    }

    function isError(ing: ParsedIngredient) {
      if (!ing?.confidence?.average) {
        return true;
      }
      return !(ing.confidence.average >= 0.75);
    }

    function asPercentage(num: number | undefined): string {
      if (!num) {
        return "0%";
      }

      return Math.round(num * 100).toFixed(2) + "%";
    }

    // =========================================================
    // Food and Ingredient Logic

    const foodStore = useFoodStore();
    const foodData = useFoodData();
    const unitStore = useUnitStore();
    const unitData = useUnitData();

    const errors = ref<Error[]>([]);

    function checkForUnit(unit?: IngredientUnit | CreateIngredientUnit) {
      // @ts-expect-error; we're just checking if there's an id on this unit and returning a boolean
      return !!unit?.id;
    }

    function checkForFood(food?: IngredientFood | CreateIngredientFood) {
      // @ts-expect-error; we're just checking if there's an id on this food and returning a boolean
      return !!food?.id;
    }

    async function createFood(food: CreateIngredientFood | undefined, index: number) {
      if (!food) {
        return;
      }

      foodData.data.name = food.name;
      parsedIng.value[index].ingredient.food = await foodStore.actions.createOne(foodData.data) || undefined;
      errors.value[index].foodError = false;

      foodData.reset();
    }

    async function createUnit(unit: CreateIngredientUnit | undefined, index: number) {
      if (!unit) {
        return;
      }

      unitData.data.name = unit.name;
      parsedIng.value[index].ingredient.unit = await unitStore.actions.createOne(unitData.data) || undefined;
      errors.value[index].unitError = false;

      unitData.reset();
    }

    function insertIngredient(index: number) {
      if (!recipe.value?.recipeIngredient) {
        return;
      }

      const ing = {
        input: "",
        confidence: {},
        ingredient: {
          quantity: 1.0,
          disableAmount: false,
          referenceId: uuid4(),
        }
      } as ParsedIngredient;

      parsedIng.value.splice(index, 0, ing);
      recipe.value.recipeIngredient.splice(index, 0, ing.ingredient);

      errors.value = parsedIng.value.map((ing, index: number) => {
        return processIngredientError(ing, index);
      });
    }

    function deleteIngredient(index: number) {
      parsedIng.value.splice(index, 1);
      recipe.value?.recipeIngredient?.splice(index, 1);

      errors.value = parsedIng.value.map((ing, index: number) => {
        return processIngredientError(ing, index);
      });
    }

    // =========================================================
    // Save All Logic
    async function saveAll() {
      const ingredients = parsedIng.value.map((ing) => {
        if (!checkForFood(ing.ingredient.food)) {
          ing.ingredient.food = undefined;
        }

        if (!checkForUnit(ing.ingredient.unit)) {
          ing.ingredient.unit = undefined;
        }

        return {
          ...ing.ingredient,
          originalText: ing.input,
        } as RecipeIngredient;
      });

      if (!recipe.value || !recipe.value.slug) {
        return;
      }

      recipe.value.recipeIngredient = ingredients;
      if (recipe.value.settings) {
        recipe.value.settings.disableAmount = false;
      }

      const { response } = await api.recipes.updateOne(recipe.value.slug, recipe.value);

      if (response?.status === 200) {
        router.push(`/g/${groupSlug.value}/r/${recipe.value.slug}`);
      }
    }

    return {
      parser,
      saveAll,
      createFood,
      createUnit,
      deleteIngredient,
      insertIngredient,
      errors,
      actions: foodStore.actions,
      workingFoodData: foodData,
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
