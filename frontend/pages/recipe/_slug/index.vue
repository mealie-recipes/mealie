<template>
  <v-container>
    <v-card v-if="skeleton" :color="`white ${false ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <v-card v-else-if="recipe">
      <!-- Recipe Header -->
      <div class="d-flex justify-end flex-wrap align-stretch">
        <v-card
          v-if="!recipe.settings.landscapeView"
          width="50%"
          flat
          class="d-flex flex-column justify-center align-center"
        >
          <v-card-text>
            <v-card-title class="headline pa-0 flex-column align-center">
              {{ recipe.name }}
              <RecipeRating :key="recipe.slug" :value="recipe.rating" :name="recipe.name" :slug="recipe.slug" />
            </v-card-title>
            <v-divider class="my-2"></v-divider>
            <VueMarkdown :source="recipe.description"> </VueMarkdown>
            <v-divider></v-divider>
            <div class="d-flex justify-center mt-5">
              <RecipeTimeCard
                class="d-flex justify-center flex-wrap"
                :class="!recipe.settings.landscapeView ? undefined : 'force-bottom'"
                :prep-time="recipe.prepTime"
                :total-time="recipe.totalTime"
                :perform-time="recipe.performTime"
              />
            </div>
          </v-card-text>
        </v-card>
        <v-img
          :key="imageKey"
          :max-width="recipe.settings.landscapeView ? null : '50%'"
          :height="hideImage ? '50' : imageHeight"
          :src="recipeImage(recipe.slug, imageKey)"
          class="d-print-none"
          @error="hideImage = true"
        >
          <RecipeTimeCard
            v-if="recipe.settings.landscapeView"
            :class="true ? undefined : 'force-bottom'"
            :prep-time="recipe.prepTime"
            :total-time="recipe.totalTime"
            :perform-time="recipe.performTime"
          />
        </v-img>
      </div>
      <v-divider></v-divider>
      <RecipeActionMenu
        v-model="form"
        :slug="recipe.slug"
        :name="recipe.name"
        :logged-in="$auth.loggedIn"
        :open="form"
        class="ml-auto"
        @close="closeEditor"
        @json="toggleJson"
        @edit="
          jsonEditor = false;
          form = true;
        "
        @save="updateRecipe(recipe.slug, recipe)"
        @delete="deleteRecipe(recipe.slug)"
      />

      <!--  Editors  -->
      <LazyRecipeJsonEditor v-if="jsonEditor" v-model="recipe" class="mt-10" :options="jsonEditorOptions" />
      <div v-else>
        <v-card-text>
          <div v-if="form" class="d-flex justify-start align-center">
            <RecipeImageUploadBtn class="my-1" :slug="recipe.slug" @upload="uploadImage" @refresh="imageKey++" />
            <RecipeSettingsMenu class="my-1 mx-1" :value="recipe.settings" @upload="uploadImage" />
          </div>
          <!-- Recipe Title Section -->
          <template v-if="!form && recipe.settings.landscapeView">
            <v-card-title class="pa-0 ma-0 headline">
              {{ recipe.name }}
            </v-card-title>
            <VueMarkdown :source="recipe.description"> </VueMarkdown>
          </template>

          <template v-else-if="form">
            <v-text-field
              v-model="recipe.name"
              class="my-3"
              :label="$t('recipe.recipe-name')"
              :rules="[validators.required]"
            >
            </v-text-field>

            <div class="d-flex flex-wrap">
              <v-text-field v-model="recipe.totalTime" class="mx-2" :label="$t('recipe.total-time')"></v-text-field>
              <v-text-field v-model="recipe.prepTime" class="mx-2" :label="$t('recipe.prep-time')"></v-text-field>
              <v-text-field v-model="recipe.performTime" class="mx-2" :label="$t('recipe.perform-time')"></v-text-field>
            </div>

            <v-textarea v-model="recipe.description" auto-grow min-height="100" :label="$t('recipe.description')">
            </v-textarea>
            <v-text-field v-model="recipe.recipeYield" dense :label="$t('recipe.servings')"> </v-text-field>
          </template>

          <!-- Advanced Editor -->
          <div v-if="form">
            <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
            <draggable v-model="recipe.recipeIngredient" handle=".handle">
              <RecipeIngredientEditor
                v-for="(ingredient, index) in recipe.recipeIngredient"
                :key="ingredient.ref"
                v-model="recipe.recipeIngredient[index]"
                :disable-amount="recipe.settings.disableAmount"
                @delete="recipe.recipeIngredient.splice(index, 1)"
              />
            </draggable>
            <div class="d-flex justify-end mt-2">
              <RecipeIngredientParserMenu :slug="recipe.slug" :ingredients="recipe.recipeIngredient" />
              <RecipeDialogBulkAdd class="ml-1 mr-1" @bulk-data="addIngredient" />
              <BaseButton @click="addIngredient"> {{ $t("general.new") }} </BaseButton>
            </div>
          </div>
          <div class="d-flex justify-space-between align-center pb-3">
            <v-tooltip v-if="!form" small top color="secondary darken-1">
              <template #activator="{ on, attrs }">
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
                  v-bind="attrs"
                  @click="scale = 1"
                  v-on="on"
                >
                  {{ scaledYield }}
                </v-btn>
              </template>
              <span> Reset Scale </span>
            </v-tooltip>

            <template v-if="!recipe.settings.disableAmount && !form">
              <v-btn color="secondary darken-1" class="mx-1" small @click="scale > 1 ? scale-- : null">
                <v-icon>
                  {{ $globals.icons.minus }}
                </v-icon>
              </v-btn>
              <v-btn color="secondary darken-1" small @click="scale++">
                <v-icon>
                  {{ $globals.icons.createAlt }}
                </v-icon>
              </v-btn>
            </template>
            <v-spacer></v-spacer>

            <RecipeRating
              v-if="recipe.settings.landscapeView"
              :key="recipe.slug"
              :value="recipe.rating"
              :name="recipe.name"
              :slug="recipe.slug"
            />
          </div>

          <v-row>
            <v-col cols="12" sm="12" md="4" lg="4">
              <RecipeIngredients
                v-if="!form"
                :value="recipe.recipeIngredient"
                :scale="scale"
                :disable-amount="recipe.settings.disableAmount"
              />

              <!-- Recipe Categories -->
              <div v-if="$vuetify.breakpoint.mdAndUp" class="mt-5">
                <v-card v-if="recipe.recipeCategory.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("recipe.categories") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeCategoryTagSelector
                      v-if="form"
                      v-model="recipe.recipeCategory"
                      :return-object="true"
                      :show-add="true"
                      :show-label="false"
                    />
                    <RecipeChips v-else :items="recipe.recipeCategory" />
                  </v-card-text>
                </v-card>

                <!-- Recipe Tags -->
                <v-card v-if="recipe.tags.length > 0 || form" class="mt-2">
                  <v-card-title class="py-2">
                    {{ $t("tag.tags") }}
                  </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text>
                    <RecipeCategoryTagSelector
                      v-if="form"
                      v-model="recipe.tags"
                      :return-object="true"
                      :show-add="true"
                      :tag-selector="true"
                      :show-label="false"
                    />
                    <RecipeChips v-else :items="recipe.tags" :is-category="false" />
                  </v-card-text>
                </v-card>

                <RecipeNutrition v-if="true || form" v-model="recipe.nutrition" class="mt-10" :edit="form" />
                <RecipeAssets
                  v-if="recipe.settings.showAssets || form"
                  v-model="recipe.assets"
                  :edit="form"
                  :slug="recipe.slug"
                />
              </div>
            </v-col>
            <v-divider v-if="$vuetify.breakpoint.mdAndUp" class="my-divider" :vertical="true"></v-divider>

            <v-col cols="12" sm="12" md="8" lg="8">
              <RecipeInstructions v-model="recipe.recipeInstructions" :edit="form" />
              <div v-if="form" class="d-flex">
                <RecipeDialogBulkAdd class="ml-auto my-2 mr-1" @bulk-data="addStep" />
                <BaseButton class="my-2" @click="addStep()"> {{ $t("general.new") }}</BaseButton>
              </div>
              <RecipeNotes v-model="recipe.notes" :edit="form" />
            </v-col>
          </v-row>

          <v-card-actions class="justify-end">
            <v-text-field
              v-if="form"
              v-model="recipe.orgURL"
              class="mt-10"
              :label="$t('recipe.original-url')"
            ></v-text-field>
            <v-btn
              v-else-if="recipe.orgURL"
              dense
              small
              :hover="false"
              type="label"
              :ripple="false"
              elevation="0"
              :href="recipe.orgURL"
              color="secondary darken-1"
              target="_blank"
              class="rounded-sm mr-4"
            >
              {{ $t("recipe.original-url") }}
            </v-btn>
          </v-card-actions>
        </v-card-text>
      </div>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import draggable from "vuedraggable";
import RecipeCategoryTagSelector from "@/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import RecipeDialogBulkAdd from "@/components/Domain/Recipe//RecipeDialogBulkAdd.vue";
import { useApiSingleton } from "~/composables/use-api";
import { validators } from "~/composables/use-validators";
import { useRecipeContext } from "~/composables/use-recipe-context";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import RecipeChips from "~/components/Domain/Recipe/RecipeChips.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeAssets from "~/components/Domain/Recipe/RecipeAssets.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import RecipeIngredientParserMenu from "~/components/Domain/Recipe/RecipeIngredientParserMenu.vue";
import { Recipe } from "~/types/api-types/recipe";
import { useStaticRoutes } from "~/composables/api";
import { uuid4 } from "~/composables/use-uuid";

export default defineComponent({
  components: {
    RecipeActionMenu,
    RecipeDialogBulkAdd,
    RecipeAssets,
    RecipeCategoryTagSelector,
    RecipeChips,
    RecipeImageUploadBtn,
    RecipeIngredients,
    RecipeInstructions,
    RecipeNotes,
    RecipeNutrition,
    RecipeRating,
    RecipeSettingsMenu,
    RecipeIngredientEditor,
    RecipeTimeCard,
    RecipeIngredientParserMenu,
    VueMarkdown,
    draggable,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useApiSingleton();

    const state = reactive({
      form: false,
      scale: 1,
      hideImage: false,
      imageKey: 1,
      loadFailed: false,
      skeleton: false,
      jsonEditor: false,
      jsonEditorOptions: {
        mode: "code",
        search: false,
        mainMenuBar: false,
      },
    });

    const { getBySlug, loading, fetchRecipe } = useRecipeContext();

    const { recipeImage } = useStaticRoutes();

    const recipe = getBySlug(slug);

    // ===========================================================================
    // Button Click Event Handlers

    async function updateRecipe(slug: string, recipe: Recipe) {
      const { data } = await api.recipes.updateOne(slug, recipe);
      state.form = false;
      if (data?.slug) {
        router.push("/recipe/" + data.slug);
      }
    }

    async function deleteRecipe(slug: string) {
      const { data } = await api.recipes.deleteOne(slug);
      if (data?.slug) {
        router.push("/");
      }
    }

    async function closeEditor() {
      state.form = false;
      state.jsonEditor = false;
      recipe.value = await fetchRecipe(slug);
    }

    function toggleJson() {
      state.jsonEditor = !state.jsonEditor;
    }

    const scaledYield = computed(() => {
      const regMatchNum = /\d+/;
      const yieldString = recipe.value?.recipeYield;
      const num = yieldString?.match(regMatchNum);

      if (num && num?.length > 0) {
        const yieldAsInt = parseInt(num[0]);
        return yieldString?.replace(num[0], String(yieldAsInt * state.scale));
      }

      return recipe.value?.recipeYield;
    });

    async function uploadImage(fileObject: File) {
      if (!recipe.value) {
        return;
      }
      const newVersion = await api.recipes.updateImage(recipe.value.slug, fileObject);
      if (newVersion?.data?.version) {
        recipe.value.image = newVersion.data.version;
      }
      state.imageKey++;
    }

    function addStep(steps: Array<string> | null = null) {
      if (!recipe.value?.recipeInstructions) {
        return;
      }

      if (steps) {
        const cleanedSteps = steps.map((step) => {
          return { text: step, title: "" };
        });

        recipe.value.recipeInstructions.push(...cleanedSteps);
      } else {
        recipe.value.recipeInstructions.push({ text: "", title: "" });
      }
    }

    function addIngredient(ingredients: Array<string> | null = null) {
      if (ingredients?.length) {
        const newIngredients = ingredients.map((x) => {
          return {
            ref: uuid4(),
            title: "",
            note: x,
            unit: null,
            food: null,
            disableAmount: true,
            quantity: 1,
          };
        });

        if (newIngredients) {
          recipe?.value?.recipeIngredient?.push(...newIngredients);
        }
      } else {
        recipe?.value?.recipeIngredient?.push({
          ref: uuid4(),
          title: "",
          note: "",
          unit: null,
          food: null,
          disableAmount: true,
          quantity: 1,
        });
      }
    }

    // ===============================================================
    // Metadata

    const structuredData = computed(() => {
      // TODO: Get this working with other scrapers, unsure why it isn't properly being delivered to clients.
      return {
        "@context": "http://schema.org",
        "@type": "Recipe",
        ...recipe.value,
      };
    });

    useMeta(() => {
      return {
        title: recipe?.value?.name || "Recipe",
        // @ts-ignore
        mainImage: recipeImage(recipe?.value?.image),
        meta: [
          {
            hid: "description",
            name: "description",
            content: recipe?.value?.description || "",
          },
        ],
        __dangerouslyDisableSanitizers: ["script"],
        script: [{ innerHTML: JSON.stringify(structuredData), type: "application/ld+json" }],
      };
    });

    return {
      scaledYield,
      toggleJson,
      ...toRefs(state),
      recipe,
      api,
      loading,
      addStep,
      deleteRecipe,
      closeEditor,
      updateRecipe,
      uploadImage,
      validators,
      recipeImage,
      addIngredient,
    };
  },
  head: {},
  computed: {
    imageHeight() {
      // @ts-ignore
      return this.$vuetify.breakpoint.xs ? "200" : "400";
    },
  },
  methods: {
    printPage() {
      window.print();
    },
  },
});
</script>

<style scoped></style>
