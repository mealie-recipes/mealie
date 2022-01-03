<template>
  <v-container
    :class="{
      'pa-0': $vuetify.breakpoint.smAndDown,
    }"
  >
    <v-card v-if="skeleton" :color="`white ${false ? 'darken-2' : 'lighten-4'}`" class="pa-3">
      <v-skeleton-loader class="mx-auto" height="700px" type="card"></v-skeleton-loader>
    </v-card>
    <v-card v-else-if="recipe" class="d-print-none">
      <!-- Recipe Header -->
      <div class="d-flex justify-end flex-wrap align-stretch">
        <v-card v-if="!enableLandscape" width="50%" flat class="d-flex flex-column justify-center align-center">
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
                :class="true ? undefined : 'force-bottom'"
                :prep-time="recipe.prepTime"
                :total-time="recipe.totalTime"
                :perform-time="recipe.performTime"
              />
            </div>
          </v-card-text>
        </v-card>
        <v-img
          :key="imageKey"
          :max-width="enableLandscape ? null : '50%'"
          :height="hideImage ? '50' : imageHeight"
          :src="recipeImage(recipe.slug, imageKey)"
          class="d-print-none"
          @error="hideImage = true"
        >
          <RecipeTimeCard
            v-if="enableLandscape"
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
        :locked="$auth.user.id !== recipe.userId && recipe.settings.locked"
        :name="recipe.name"
        :logged-in="$auth.loggedIn"
        :open="form"
        :recipe-id="recipe.id"
        class="ml-auto"
        @close="closeEditor"
        @json="toggleJson"
        @edit="
          jsonEditor = false;
          form = true;
        "
        @save="updateRecipe(recipe.slug, recipe)"
        @delete="deleteRecipe(recipe.slug)"
        @print="printRecipe"
      />

      <!--  Editors  -->
      <LazyRecipeJsonEditor v-if="jsonEditor" v-model="recipe" class="mt-10" :options="jsonEditorOptions" />
      <div v-else>
        <v-card-text
          :class="{
            'px-2': $vuetify.breakpoint.smAndDown,
          }"
        >
          <div v-if="form" class="d-flex justify-start align-center">
            <RecipeImageUploadBtn class="my-1" :slug="recipe.slug" @upload="uploadImage" @refresh="imageKey++" />
            <RecipeSettingsMenu class="my-1 mx-1" :value="recipe.settings" :is-owner="recipe.userId == $auth.user.id" @upload="uploadImage" />
          </div>
          <!-- Recipe Title Section -->
          <template v-if="!form && enableLandscape">
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
            <draggable v-if="recipe.recipeIngredient.length > 0" v-model="recipe.recipeIngredient" handle=".handle">
              <RecipeIngredientEditor
                v-for="(ingredient, index) in recipe.recipeIngredient"
                :key="ingredient.referenceId"
                v-model="recipe.recipeIngredient[index]"
                :disable-amount="recipe.settings.disableAmount"
                @delete="recipe.recipeIngredient.splice(index, 1)"
              />
            </draggable>
            <v-skeleton-loader v-else boilerplate elevation="2" type="list-item"> </v-skeleton-loader>
            <div class="d-flex justify-end mt-2">
              <v-tooltip top color="accent">
                <template #activator="{ on, attrs }">
                  <span v-on="on">
                    <BaseButton
                      :disabled="recipe.settings.disableAmount"
                      color="accent"
                      :to="`${recipe.slug}/ingredient-parser`"
                      v-bind="attrs"
                    >
                      <template #icon>
                        {{ $globals.icons.foods }}
                      </template>
                      Parse
                    </BaseButton>
                  </span>
                </template>
                <span>{{
                  recipe.settings.disableAmount ? "Enable ingredient amounts to use this feature" : "Parse ingredients"
                }}</span>
              </v-tooltip>
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
              v-if="enableLandscape"
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

              <!-- Recipe Tools Display -->
              <div v-if="!form && recipe.tools && recipe.tools.length > 0">
                <h2 class="mb-2 mt-4">Required Tools</h2>
                <v-list-item v-for="(tool, index) in recipe.tools" :key="index" dense>
                  <v-checkbox
                    v-model="recipe.tools[index].onHand"
                    hide-details
                    class="pt-0 my-auto py-auto"
                    color="secondary"
                    @change="updateTool(recipe.tools[index])"
                  >
                  </v-checkbox>
                  <v-list-item-content>
                    {{ tool.name }}
                  </v-list-item-content>
                </v-list-item>
              </div>

              <div v-if="$vuetify.breakpoint.mdAndUp" class="mt-5">
                <!-- Recipe Categories -->
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

                <!-- Recipe Tools Edit -->
                <v-card v-if="form" class="mt-2">
                  <v-card-title class="py-2"> Required Tools </v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text class="pt-0">
                    <RecipeTools v-model="recipe.tools" :edit="form" />
                  </v-card-text>
                </v-card>

                <RecipeNutrition
                  v-if="recipe.settings.showNutrition"
                  v-model="recipe.nutrition"
                  class="mt-10"
                  :edit="form"
                />
                <client-only>
                  <RecipeAssets
                    v-if="recipe.settings.showAssets"
                    v-model="recipe.assets"
                    :edit="form"
                    :slug="recipe.slug"
                  />
                </client-only>
              </div>
            </v-col>
            <v-divider v-if="$vuetify.breakpoint.mdAndUp" class="my-divider" :vertical="true"></v-divider>

            <v-col cols="12" sm="12" md="8" lg="8">
              <RecipeInstructions
                v-model="recipe.recipeInstructions"
                :ingredients="recipe.recipeIngredient"
                :disable-amount="recipe.settings.disableAmount"
                :edit="form"
              />
              <div v-if="form" class="d-flex">
                <RecipeDialogBulkAdd class="ml-auto my-2 mr-1" @bulk-data="addStep" />
                <BaseButton class="my-2" @click="addStep()"> {{ $t("general.new") }}</BaseButton>
              </div>

              <!-- TODO: Somehow fix duplicate code for mobile/desktop -->
              <div v-if="!$vuetify.breakpoint.mdAndUp" class="mt-5">
                <!-- Recipe Tools Edit -->
                <v-card v-if="form">
                  <v-card-title class="py-2"> Required Tools</v-card-title>
                  <v-divider class="mx-2"></v-divider>
                  <v-card-text class="pt-0">
                    <RecipeTools v-model="recipe.tools" :edit="form" />
                  </v-card-text>
                </v-card>

                <!-- Recipe Categories -->
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

                <RecipeNutrition
                  v-if="recipe.settings.showNutrition"
                  v-model="recipe.nutrition"
                  class="mt-10"
                  :edit="form"
                />
                <client-only>
                  <RecipeAssets
                    v-if="recipe.settings.showAssets"
                    v-model="recipe.assets"
                    :edit="form"
                    :slug="recipe.slug"
                  />
                </client-only>
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
      <v-card v-if="form && $auth.user.advanced" flat class="ma-2 mb-2">
        <v-card-title> API Extras </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text>
          Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs
          within a recipe to reference from 3rd part applications. You can use these keys to contain information to
          trigger automation or custom messages to relay to your desired device.
          <v-row v-for="(value, key) in recipe.extras" :key="key" class="mt-1">
            <v-col cols="8">
              <v-text-field v-model="recipe.extras[key]" dense :label="key">
                <template #prepend>
                  <v-btn color="error" icon class="mt-n4" @click="removeApiExtra(key)">
                    <v-icon> {{ $globals.icons.delete }} </v-icon>
                  </v-btn>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="d-flex">
          <div style="max-width: 200px">
            <v-text-field v-model="apiNewKey" label="Message Key"></v-text-field>
          </div>
          <BaseButton create small class="ml-5" @click="createApiExtra" />
        </v-card-actions>
      </v-card>
    </v-card>
    <RecipeComments
      v-if="recipe && !recipe.settings.disableComments && !form"
      v-model="recipe.comments"
      :slug="recipe.slug"
      :recipe-id="recipe.id"
      class="mt-4"
    />
    <RecipePrintView v-if="recipe" :recipe="recipe" />
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  reactive,
  ref,
  toRefs,
  useContext,
  useMeta,
  useRoute,
  useRouter,
  onMounted,
} from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import draggable from "vuedraggable";
import { invoke, until } from "@vueuse/core";
import RecipeCategoryTagSelector from "@/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import RecipeDialogBulkAdd from "@/components/Domain/Recipe//RecipeDialogBulkAdd.vue";
import { useUserApi, useStaticRoutes } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { useRecipe, useRecipeMeta } from "~/composables/recipes";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import RecipeChips from "~/components/Domain/Recipe/RecipeChips.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import RecipePrintView from "~/components/Domain/Recipe/RecipePrintView.vue";
import RecipeTools from "~/components/Domain/Recipe/RecipeTools.vue";
import RecipeComments from "~/components/Domain/Recipe/RecipeComments.vue";
import { Recipe } from "~/types/api-types/recipe";
import { uuid4, deepCopy } from "~/composables/use-utils";
import { Tool } from "~/api/class-interfaces/tools";
import { useRouteQuery } from "~/composables/use-router";

export default defineComponent({
  components: {
    draggable,
    RecipeActionMenu,
    RecipeAssets: () => {
      if (process.client) {
        return import(/* webpackChunkName: "RecipeAssets" */ "~/components/Domain/Recipe/RecipeAssets.vue");
      }
    },
    RecipeCategoryTagSelector,
    RecipeChips,
    RecipeComments,
    RecipeDialogBulkAdd,
    RecipeImageUploadBtn,
    RecipeIngredientEditor,
    RecipeIngredients,
    RecipeInstructions,
    RecipeNotes,
    RecipeNutrition,
    RecipePrintView,
    RecipeRating,
    RecipeSettingsMenu,
    RecipeTimeCard,
    RecipeTools,
    VueMarkdown,
  },
  async beforeRouteLeave(_to, _from, next) {
    const isSame = JSON.stringify(this.recipe) === JSON.stringify(this.originalRecipe);

    console.log({ working: this.recipe, saved: this.originalRecipe });

    if (this.form && !isSame) {
      if (window.confirm("You have unsaved changes. Do you want to save before leaving?")) {
        // @ts-ignore
        await this.api.recipes.updateOne(this.recipe.slug, this.recipe);
      }
    }
    next();
  },

  setup() {
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useUserApi();

    // ===============================================================
    // Edit on Navigate

    const edit = useRouteQuery("edit", "");

    onMounted(() => {
      console.log("edit", edit.value);
      if (edit.value) {
        console.log("edit", edit.value);
        state.form = edit.value === "true";
      }
    });

    // ===============================================================
    // Check Before Leaving

    const domSaveChangesDialog = ref(null);

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

    const { recipe, loading, fetchRecipe } = useRecipe(slug);

    // Manage a deep copy of the recipe so we can detect if changes have occurred and inform
    // the user if they try to navigate away from the page without saving.
    const originalRecipe = ref<Recipe | null>(null);

    invoke(async () => {
      await until(recipe).not.toBeNull();

      originalRecipe.value = deepCopy(recipe.value);
    });

    const { recipeImage } = useStaticRoutes();

    const { $vuetify } = useContext();

    // ===========================================================================
    // Layout Helpers

    const enableLandscape = computed(() => {
      const preferLandscape = recipe?.value?.settings?.landscapeView;
      const smallScreen = !$vuetify.breakpoint.smAndUp;

      if (preferLandscape) {
        return true;
      } else if (smallScreen) {
        return true;
      }

      return false;
    });

    // ===========================================================================
    // Button Click Event Handlers

    async function updateRecipe(slug: string, recipe: Recipe) {
      const { data } = await api.recipes.updateOne(slug, recipe);
      state.form = false;
      state.jsonEditor = false;
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
      await fetchRecipe();
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
          return { id: uuid4(), text: step, title: "", ingredientReferences: [] };
        });

        recipe.value.recipeInstructions.push(...cleanedSteps);
      } else {
        recipe.value.recipeInstructions.push({ id: uuid4(), text: "", title: "", ingredientReferences: [] });
      }
    }

    function addIngredient(ingredients: Array<string> | null = null) {
      if (ingredients?.length) {
        const newIngredients = ingredients.map((x) => {
          return {
            referenceId: uuid4(),
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
          referenceId: uuid4(),
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
    // Recipe Tools

    async function updateTool(tool: Tool) {
      const { response } = await api.tools.updateOne(tool.id, tool);

      if (response?.status === 200) {
        console.log("Update Successful");
      }
    }

    // ===============================================================
    // Recipe API Extras

    const apiNewKey = ref("");

    function createApiExtra() {
      if (!recipe.value) {
        return;
      }

      if (!recipe.value.extras) {
        recipe.value.extras = {};
      }

      // check for duplicate keys
      if (Object.keys(recipe.value.extras).includes(apiNewKey.value)) {
        return;
      }

      recipe.value.extras[apiNewKey.value] = "";

      apiNewKey.value = "";
    }

    function removeApiExtra(key: string) {
      if (!recipe.value) {
        return;
      }

      if (!recipe.value.extras) {
        return;
      }

      delete recipe.value.extras[key];
      recipe.value.extras = { ...recipe.value.extras };
    }

    // ===============================================================
    // Metadata

    // @ts-ignore
    const metaData = useRecipeMeta(recipe);

    useMeta(metaData);

    return {
      createApiExtra,
      apiNewKey,
      originalRecipe,
      domSaveChangesDialog,
      enableLandscape,
      scaledYield,
      toggleJson,
      ...toRefs(state),
      recipe,
      api,
      loading,
      addStep,
      deleteRecipe,
      closeEditor,
      updateTool,
      updateRecipe,
      uploadImage,
      validators,
      recipeImage,
      addIngredient,
      removeApiExtra,
    };
  },
  head: {},
  computed: {
    imageHeight() {
      return this.$vuetify.breakpoint.xs ? "200" : "400";
    },
  },
  methods: {
    printRecipe() {
      window.print();
    },
  },
});
</script>

