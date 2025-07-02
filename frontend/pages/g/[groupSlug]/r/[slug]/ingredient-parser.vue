<template>
  <v-container v-if="recipe">
    <v-container>
      <BaseCardSectionTitle :title="$t('recipe.parser.ingredient-parser')">
        <div class="mt-4">
          {{ $t("recipe.parser.explanation") }}
        </div>

        <div class="my-4">
          {{ $t("recipe.parser.alerts-explainer") }}
        </div>
        <div class="d-flex align-center mb-n4">
          <div class="mb-4">
            {{ $t("recipe.parser.select-parser") }}
          </div>
          <BaseOverflowButton
            v-model="parser"
            btn-class="mx-2 mb-4"
            :items="availableParsers"
          />
        </div>
      </BaseCardSectionTitle>

      <div
        class="d-flex mt-n3 mb-4 justify-end"
        style="gap: 5px"
      >
        <BaseButton
          cancel
          class="mr-auto"
          @click="$router.go(-1)"
        />
        <BaseButton
          color="info"
          :disabled="parserLoading"
          @click="fetchParsed"
        >
          <template #icon>
            {{ $globals.icons.foods }}
          </template>
          {{ $t("recipe.parser.parse-all") }}
        </BaseButton>
        <BaseButton
          save
          :disabled="parserLoading"
          @click="saveAll"
        />
      </div>

      <div v-if="parserLoading">
        <AppLoader
          v-if="parserLoading"
          :loading="parserLoading"
          waiting-text=""
        />
      </div>
      <div v-else>
        <v-expansion-panels
          v-model="panels"
          multiple
        >
          <VueDraggable
            v-if="parsedIng.length > 0"
            v-model="parsedIng"
            handle=".handle"
            :delay="250"
            :delay-on-touch-only="true"
            :style="{ width: '100%' }"
            ghost-class="ghost"
          >
            <v-expansion-panel
              v-for="(ing, index) in parsedIng"
              :key="index"
            >
              <v-expansion-panel-title
                class="my-0 py-0"
                disable-icon-rotate
              >
                <template #default="{ expanded }">
                  <v-fade-transition>
                    <span
                      v-if="!expanded"
                      key="0"
                    > {{ ing.input }} </span>
                  </v-fade-transition>
                </template>
                <template #actions>
                  <v-icon
                    start
                    :color="isError(ing) ? 'error' : 'success'"
                  >
                    {{ isError(ing) ? $globals.icons.alert : $globals.icons.check }}
                  </v-icon>
                  <div
                    class="my-auto"
                    :color="isError(ing) ? 'error-text' : 'success-text'"
                  >
                    {{ ing.confidence ? asPercentage(ing.confidence.average!) : "" }}
                  </div>
                </template>
              </v-expansion-panel-title>
              <v-expansion-panel-text class="pb-0 mb-0">
                <RecipeIngredientEditor
                  v-model="parsedIng[index].ingredient"
                  allow-insert-ingredient
                  @insert-ingredient="insertIngredient(index)"
                  @delete="deleteIngredient(index)"
                />
                {{ ing.input }}
                <v-card-actions>
                  <v-spacer />
                  <BaseButton
                    v-if="errors[index].unitError && errors[index].unitErrorMessage !== ''"
                    color="warning"
                    size="small"
                    @click="createUnit(ing.ingredient.unit!, index)"
                  >
                    {{ errors[index].unitErrorMessage }}
                  </BaseButton>
                  <BaseButton
                    v-if="errors[index].foodError && errors[index].foodErrorMessage !== ''"
                    color="warning"
                    size="small"
                    @click="createFood(ing.ingredient.food!, index)"
                  >
                    {{ errors[index].foodErrorMessage }}
                  </BaseButton>
                </v-card-actions>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </VueDraggable>
        </v-expansion-panels>
      </div>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { invoke, until } from "@vueuse/core";
import { VueDraggable } from "vue-draggable-plus";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import { alert } from "~/composables/use-toast";
import { useAppInfo, useUserApi } from "~/composables/api";
import { useRecipe } from "~/composables/recipes";
import { useFoodData, useFoodStore, useUnitData, useUnitStore } from "~/composables/store";
import { useParsingPreferences } from "~/composables/use-users/preferences";
import { uuid4 } from "~/composables/use-utils";
import type {
  CreateIngredientFood,
  CreateIngredientUnit,
  IngredientFood,
  IngredientUnit,
  ParsedIngredient,
  RecipeIngredient,
} from "~/lib/api/types/recipe";
import type { Parser } from "~/lib/api/user/recipes/recipe";

interface Error {
  ingredientIndex: number;
  unitError: boolean;
  unitErrorMessage: string;
  foodError: boolean;
  foodErrorMessage: string;
}

export default defineNuxtComponent({
  components: {
    RecipeIngredientEditor,
    VueDraggable,
  },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const panels = ref<number[]>([]);

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

    const router = useRouter();
    const slug = route.params.slug as string;
    const api = useUserApi();
    const appInfo = useAppInfo();

    const { recipe, loading } = useRecipe(slug);
    const parserLoading = ref(false);

    invoke(async () => {
      await until(recipe).not.toBeNull();

      fetchParsed();
    });

    const ingredients = ref<any[]>([]);

    const availableParsers = computed(() => {
      return [
        {
          text: i18n.t("recipe.parser.natural-language-processor"),
          value: "nlp",
        },
        {
          text: i18n.t("recipe.parser.brute-parser"),
          value: "brute",
        },
        {
          text: i18n.t("recipe.parser.openai-parser"),
          value: "openai",
          hide: !appInfo.value?.enableOpenai,
        },
      ];
    });

    // =========================================================
    // Parser Logic
    const parserPreferences = useParsingPreferences();
    const parser = ref<Parser>(parserPreferences.value.parser || "nlp");
    const parsedIng = ref<ParsedIngredient[]>([]);
    watch(parser, (val) => {
      parserPreferences.value.parser = val;
    });

    function processIngredientError(ing: ParsedIngredient, index: number): Error {
      const unitError = !checkForUnit(ing.ingredient.unit!);
      const foodError = !checkForFood(ing.ingredient.food!);

      let unitErrorMessage = "";
      let foodErrorMessage = "";

      if (unitError || foodError) {
        if (unitError) {
          if (ing?.ingredient?.unit?.name) {
            const unit = ing.ingredient.unit.name || i18n.t("recipe.parser.no-unit");
            unitErrorMessage = i18n.t("recipe.parser.missing-unit", { unit }).toString();
          }
        }

        if (foodError) {
          if (ing?.ingredient?.food?.name) {
            const food = ing.ingredient.food.name || i18n.t("recipe.parser.no-food");
            foodErrorMessage = i18n.t("recipe.parser.missing-food", { food }).toString();
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
      const raw = recipe.value.recipeIngredient.map(ing => ing.note ?? "");

      parserLoading.value = true;
      const { data } = await api.recipes.parseIngredients(parser.value, raw);
      parserLoading.value = false;

      if (data) {
        // When we send the recipe ingredient text to be parsed, we lose the reference to the original unparsed ingredient.
        // Generally this is fine, but if the unparsed ingredient had a title, we lose it; we add back the title for each ingredient here.
        try {
          for (let i = 0; i < recipe.value.recipeIngredient.length; i++) {
            data[i].ingredient.title = recipe.value.recipeIngredient[i].title;
          }
        }
        catch {
          console.error("Index Mismatch Error during recipe ingredient parsing; did the number of ingredients change?");
        }

        parsedIng.value = data;

        errors.value = data.map((ing, index: number) => {
          return processIngredientError(ing, index);
        });
      }
      else {
        alert.error(i18n.t("events.something-went-wrong") as string);
        parsedIng.value = [];
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
      return !!unit?.id;
    }

    function checkForFood(food?: IngredientFood | CreateIngredientFood) {
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
        },
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
        if (!checkForFood(ing.ingredient.food!)) {
          ing.ingredient.food = undefined;
        }

        if (!checkForUnit(ing.ingredient.unit!)) {
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

    useSeoMeta({
      title: i18n.t("recipe.parser.ingredient-parser"),
    });

    return {
      parser,
      availableParsers,
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
      parserLoading,
      ingredients,
    };
  },
});
</script>
