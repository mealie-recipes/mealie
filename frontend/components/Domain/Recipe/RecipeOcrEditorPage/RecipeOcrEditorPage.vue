<template>
  <v-container
    v-if="recipe && recipe.slug && recipe.settings && recipe.recipeIngredient"
    :class="{
      'pa-0': $vuetify.breakpoint.smAndDown,
    }"
  >
    <BannerExperimental />

    <div v-if="loading">
      <v-spacer />
      <v-progress-circular indeterminate class="" color="primary"> </v-progress-circular>
      {{ loadingText }}
      <v-spacer />
    </div>
    <v-row v-if="!loading">
      <v-col cols="12" sm="7" md="7" lg="7">
        <RecipeOcrEditorPageCanvas
          :image="canvasImage"
          :tsv="tsv"
          @setText="canvasSetText"
          @update-recipe="updateRecipe"
          @close-editor="closeEditor"
          @text-selected="updateSelectedText"
        >
        </RecipeOcrEditorPageCanvas>

        <RecipeOcrEditorPageHelp />
      </v-col>
      <v-col cols="12" sm="5" md="5" lg="5">
        <v-tabs v-model="tab" fixed-tabs>
          <v-tab key="header">
            {{ $t("general.recipe") }}
          </v-tab>
          <v-tab key="ingredients">
            {{ $t("recipe.ingredients") }}
          </v-tab>
          <v-tab key="instructions">
            {{ $t("recipe.instructions") }}
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item key="header">
            <v-text-field
              v-model="recipe.name"
              class="my-3"
              :label="$t('recipe.recipe-name')"
              :rules="[validators.required]"
              @focus="selectedRecipeField = 'name'"
            >
            </v-text-field>

            <div class="d-flex flex-wrap">
              <v-text-field
                v-model="recipe.totalTime"
                class="mx-2"
                :label="$t('recipe.total-time')"
                @click="selectedRecipeField = 'totalTime'"
              ></v-text-field>
              <v-text-field
                v-model="recipe.prepTime"
                class="mx-2"
                :label="$t('recipe.prep-time')"
                @click="selectedRecipeField = 'prepTime'"
              ></v-text-field>
              <v-text-field
                v-model="recipe.performTime"
                class="mx-2"
                :label="$t('recipe.perform-time')"
                @click="selectedRecipeField = 'performTime'"
              ></v-text-field>
            </div>

            <v-textarea
              v-model="recipe.description"
              auto-grow
              min-height="100"
              :label="$t('recipe.description')"
              @click="selectedRecipeField = 'description'"
            >
            </v-textarea>
            <v-text-field
              v-model="recipe.recipeYield"
              dense
              :label="$t('recipe.servings')"
              @click="selectedRecipeField = 'recipeYield'"
            >
            </v-text-field>
          </v-tab-item>
          <v-tab-item key="ingredients">
            <div class="d-flex justify-end mt-2">
              <RecipeDialogBulkAdd class="ml-1 mr-1" :input-text-prop="canvasSelectedText" @bulk-data="addIngredient" />
              <BaseButton @click="addIngredient"> {{ $t("general.new") }} </BaseButton>
            </div>
            <draggable
              v-if="recipe.recipeIngredient.length > 0"
              v-model="recipe.recipeIngredient"
              handle=".handle"
              v-bind="{
                animation: 200,
                group: 'description',
                disabled: false,
                ghostClass: 'ghost',
              }"
              @start="drag = true"
              @end="drag = false"
            >
              <TransitionGroup type="transition" :name="!drag ? 'flip-list' : ''">
                <RecipeIngredientEditor
                  v-for="(ingredient, index) in recipe.recipeIngredient"
                  :key="ingredient.referenceId"
                  v-model="recipe.recipeIngredient[index]"
                  class="list-group-item"
                  :disable-amount="recipe.settings.disableAmount"
                  @delete="recipe.recipeIngredient.splice(index, 1)"
                  @clickIngredientField="setSingleIngredient($event, index)"
                />
              </TransitionGroup>
            </draggable>
          </v-tab-item>
          <v-tab-item key="instructions">
            <div class="d-flex justify-end mt-2">
              <RecipeDialogBulkAdd class="ml-1 mr-1" :input-text-prop="canvasSelectedText" @bulk-data="addStep" />
              <BaseButton @click="addStep()"> {{ $t("general.new") }}</BaseButton>
            </div>
            <RecipeInstructions
              v-model="recipe.recipeInstructions"
              :ingredients="recipe.recipeIngredient"
              :disable-amount="recipe.settings.disableAmount"
              :edit="true"
              :recipe-id="recipe.id"
              :recipe-slug="recipe.slug"
              :assets.sync="recipe.assets"
              @clickInstructionField="setSingleStep"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, toRefs, useRouter } from "@nuxtjs/composition-api";
import { until } from "@vueuse/core";
import { invoke } from "@vueuse/shared";
import draggable from "vuedraggable";
import { useUserApi, useStaticRoutes } from "~/composables/api";
import { OcrTsvResponse as NullableOcrTsvResponse } from "~/lib/api/types/ocr";
import { validators } from "~/composables/use-validators";
import { Recipe, RecipeIngredient, RecipeStep } from "~/lib/api/types/recipe";
import { Paths, Leaves, SelectedRecipeLeaves } from "~/types/ocr-types";
import BannerExperimental from "~/components/global/BannerExperimental.vue";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import RecipeOcrEditorPageCanvas from "~/components/Domain/Recipe/RecipeOcrEditorPage/RecipeOcrEditorPageParts/RecipeOcrEditorPageCanvas.vue";
import RecipeOcrEditorPageHelp from "~/components/Domain/Recipe/RecipeOcrEditorPage/RecipeOcrEditorPageParts/RecipeOcrEditorPageHelp.vue";
import { uuid4 } from "~/composables/use-utils";
import { NoUndefinedField } from "~/lib/api/types/non-generated";

// Temporary Shim until we have a better solution
// https://github.com/phillipdupuis/pydantic-to-typescript/issues/28
type OcrTsvResponse = NoUndefinedField<NullableOcrTsvResponse>;

export default defineComponent({
  components: {
    RecipeIngredientEditor,
    draggable,
    BannerExperimental,
    RecipeDialogBulkAdd,
    RecipeInstructions,
    RecipeOcrEditorPageCanvas,
    RecipeOcrEditorPageHelp,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const router = useRouter();
    const api = useUserApi();

    const tsv = ref<OcrTsvResponse[]>([]);

    const drag = ref(false);

    const { recipeAssetPath } = useStaticRoutes();

    function assetURL(assetName: string) {
      return recipeAssetPath(props.recipe.id, assetName);
    }

    const state = reactive({
      loading: true,
      loadingText: "Loading recipe...",
      tab: null,
      selectedRecipeField: "" as SelectedRecipeLeaves | "",
      canvasSelectedText: "",
      canvasImage: new Image(),
    });

    const setPropertyValueByPath = function <T extends Recipe>(object: T, path: Paths<T>, value: any) {
      const a = path.split(".");
      let nextProperty: any = object;
      for (let i = 0, n = a.length - 1; i < n; ++i) {
        const k = a[i];
        if (k in nextProperty) {
          nextProperty = nextProperty[k];
        } else {
          return;
        }
      }
      nextProperty[a[a.length - 1]] = value;
    };

    /**
     * This function will find the title of a recipe with the assumption that the title
     * has the biggest ratio of surface area / number of words on the image.
     * @return Returns the text parts of the block with the highest score.
     */
    function findRecipeTitle() {
      const filtered = tsv.value.filter((element) => element.level === 2 || element.level === 5);
      const blocks = [[]] as OcrTsvResponse[][];
      let blockNum = 1;
      filtered.forEach((element, index, array) => {
        if (index !== 0 && array[index - 1].blockNum !== element.blockNum) {
          blocks.push([]);
          blockNum = element.blockNum;
        }
        blocks[blockNum - 1].push(element);
      });

      let bestScore = 0;
      let bestBlock = blocks[0];
      blocks.forEach((element) => {
        // element[0] is the block declaration line containing the blocks total dimensions
        // element.length is the number of words (+ 2) contained in that block
        const elementScore = (element[0].height * element[0].width) / element.length; // Prettier is adding useless parenthesis for a mysterious reason
        const elementText = element.map((element) => element.text).join(""); // Identify empty blocks and don't count them
        if (elementScore > bestScore && elementText !== "") {
          bestBlock = element;
          bestScore = elementScore;
        }
      });

      return bestBlock
        .filter((element) => element.level === 5 && element.conf >= 40)
        .map((element) => {
          return element.text.trim();
        })
        .join(" ");
    }

    onMounted(() => {
      invoke(async () => {
        await until(props.recipe).not.toBeNull();
        state.loadingText = "Loading OCR data...";

        const assetName = props.recipe.assets[0].fileName;
        const imagesrc = assetURL(assetName);
        state.canvasImage.src = imagesrc;

        const res = await api.ocr.assetToTsv(props.recipe.slug, assetName);
        tsv.value = res.data as OcrTsvResponse[];
        state.loading = false;

        if (props.recipe.name.match(/New\sOCR\sRecipe(\s\([0-9]+\))?/g)) {
          props.recipe.name = findRecipeTitle();
        }
      });
    });

    function addIngredient(ingredients: Array<string> | null = null) {
      if (ingredients?.length) {
        const newIngredients = ingredients.map((x) => {
          return {
            referenceId: uuid4(),
            title: "",
            note: x,
            unit: undefined,
            food: undefined,
            disableAmount: true,
            quantity: 1,
            originalText: "",
          };
        });

        if (newIngredients) {
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          props.recipe.recipeIngredient.push(...newIngredients);
        }
      } else {
        props.recipe.recipeIngredient.push({
          referenceId: uuid4(),
          title: "",
          note: "",
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          unit: undefined,
          // @ts-expect-error - prop can be null-type by NoUndefinedField type forces it to be set
          food: undefined,
          disableAmount: true,
          quantity: 1,
        });
      }
    }

    function addStep(steps: Array<string> | null = null) {
      if (!props.recipe.recipeInstructions) {
        return;
      }

      if (steps) {
        const cleanedSteps = steps.map((step) => {
          return { id: uuid4(), text: step, title: "", ingredientReferences: [] };
        });

        props.recipe.recipeInstructions.push(...cleanedSteps);
      } else {
        props.recipe.recipeInstructions.push({ id: uuid4(), text: "", title: "", ingredientReferences: [] });
      }
    }

    //  EVENT HANDLERS

    // Canvas component event handlers
    async function updateRecipe() {
      const { data } = await api.recipes.updateOne(props.recipe.slug, props.recipe);
      if (data?.slug) {
        router.push("/recipe/" + data.slug);
      }
    }

    function closeEditor() {
      router.push("/recipe/" + props.recipe.slug);
    }

    const canvasSetText = function () {
      if (state.selectedRecipeField !== "") {
        setPropertyValueByPath<Recipe>(props.recipe, state.selectedRecipeField, state.canvasSelectedText);
      }
    };

    function updateSelectedText(value: string) {
      state.canvasSelectedText = value;
    }

    // Recipe field selection event handlers
    function setSingleIngredient(f: keyof RecipeIngredient, index: number) {
      state.selectedRecipeField = `recipeIngredient.${index}.${f}` as SelectedRecipeLeaves;
    }

    // Leaves<RecipeStep[]> will return some function types making eslint very unhappy
    type RecipeStepsLeaves = `${number}.${Leaves<RecipeStep>}`;

    function setSingleStep(path: RecipeStepsLeaves) {
      state.selectedRecipeField = `recipeInstructions.${path}` as SelectedRecipeLeaves;
    }

    return {
      ...toRefs(state),
      addIngredient,
      addStep,
      drag,
      assetURL,
      updateRecipe,
      closeEditor,
      updateSelectedText,
      tsv,
      validators,
      setSingleIngredient,
      setSingleStep,
      canvasSetText,
    };
  },
});
</script>

<style lang="css">
.ghost {
  opacity: 0.5;
}
</style>
