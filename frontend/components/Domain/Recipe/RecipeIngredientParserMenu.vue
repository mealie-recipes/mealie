<template>
  <div>
    <v-menu offset-y offset-overflow left top nudge-top="6" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on">
          <v-icon left>
            {{ $globals.icons.foods }}
          </v-icon>
          Parse
        </v-btn>
      </template>
      <v-card width="400">
        <v-card-title class="mb-1 pb-0">
          <v-icon left color="warning"> {{ $globals.icons.alert }}</v-icon> Experimental
        </v-card-title>
        <v-divider class="mx-2"> </v-divider>
        <v-card-text>
          Mealie can use natural language processing to attempt to parse and create units, and foods for your Recipe
          ingredients. This is experimental and may not work as expected. If you choose to not use the parsed results
          you can click the close button at the top of the page and your changes will not be saved.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <BaseButton small color="accent" @click="parseIngredients">
            <template #icon>
              {{ $globals.icons.check }}
            </template>
            {{ $t("general.confirm") }}
          </BaseButton>
        </v-card-actions>
      </v-card>
    </v-menu>
    <BaseDialog ref="domParsedDataDialog" width="100%">
      <v-card-text>
        <v-expansion-panels v-model="panels" multiple>
          <v-expansion-panel v-for="(ing, index) in parsedData.ingredient" :key="index">
            <v-expansion-panel-header class="my-0 py-0">
              <div class="text-body-1">
                <span>
                  <v-icon v-if="errors[index].foodError" color="warning">
                    {{ $globals.icons.close }}
                  </v-icon>
                  <v-icon v-else color="success">
                    {{ $globals.icons.check }}
                  </v-icon>
                </span>
                {{ ingredients[index].note }}
              </div>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="pb-0 mb-0">
              <RecipeIngredientEditor v-model="parsedData.ingredient[index]" />
              <v-card-actions>
                <v-spacer></v-spacer>
                <BaseButton v-if="errors[index].foodError" color="warning" small @click="createFood(ing.food, index)">
                  {{ errors[index].foodErrorMessage }}
                </BaseButton>
              </v-card-actions>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import RecipeIngredientEditor from "./RecipeIngredientEditor.vue";
import { useApiSingleton } from "~/composables/use-api";
import { RecipeIngredient, RecipeIngredientUnit } from "~/types/api-types/recipe";
import { useFoods } from "~/composables/use-recipe-foods";
import { useUnits } from "~/composables/use-recipe-units";
import { Food } from "~/api/class-interfaces/recipe-foods";

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
  props: {
    ingredients: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const ingredients = props.ingredients;
    const api = useApiSingleton();

    const parsedData = ref<any>([]);

    const { foods, workingFoodData, actions } = useFoods();
    const { units } = useUnits();

    const domParsedDataDialog = ref(null);

    const panels = ref<number[]>([]);
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

      parsedData.value[index] = await actions.createOne();

      errors.value[index].foodError = false;
    }

    async function parseIngredients() {
      // @ts-ignore -> No idea what it's talking about
      const ingredientNotes = ingredients.map((ing: RecipeIngredient) => ing.note);

      const { data } = await api.recipes.parseIngredients(ingredientNotes);

      if (data) {
        // @ts-ignore
        domParsedDataDialog.value.open();
        console.log(data);
        parsedData.value = data;

        // @ts-ignore
        errors.value = data.ingredient.map((ing, index: number) => {
          const unitError = !checkForUnit(ing.unit);
          const foodError = !checkForFood(ing.food);

          let unitErrorMessage = "";
          let foodErrorMessage = "";

          if (unitError || foodError) {
            if (unitError) {
              unitErrorMessage = `Create missing unit '${ing.unit.name || "No unit"}'`;
            }

            if (foodError) {
              panels.value.push(index);
              foodErrorMessage = `Create missing food '${ing.food.name || "No food"}'?`;
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

    return { api, parseIngredients, parsedData, domParsedDataDialog, panels, errors, createFood };
  },
});
</script>
