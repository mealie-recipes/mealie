<template>
  <div>
    <v-container v-show="!isCookMode" key="recipe-page" :class="{ 'pa-0': $vuetify.breakpoint.smAndDown }">
      <v-card :flat="$vuetify.breakpoint.smAndDown" class="d-print-none">
        <RecipePageHeader
          :recipe="recipe"
          :recipe-scale="scale"
          :landscape="landscape"
          @save="saveRecipe"
          @delete="deleteRecipe"
        />
        <LazyRecipeJsonEditor v-if="isEditJSON" v-model="recipe" class="mt-10" :options="EDITOR_OPTIONS" />
        <v-card-text v-else>
          <!--
            This is where most of the main content is rendered. Some components include state for both Edit and View modes
            which is why some have explicit v-if statements and others use the composition API to determine and manage
            the shared state internally.

            The global recipe object is shared down the tree of components and _is_ mutated by child components. This is
            some-what of a hack of the system and goes against the principles of Vue, but it _does_ seem to work and streamline
            a significant amount of prop management. When we move to Vue 3 and have access to some of the newer API's the plan to update this
            data management and mutation system we're using.
          -->
          <RecipePageInfoEditor v-if="isEditMode" :recipe="recipe" :landscape="landscape" />
          <RecipePageEditorToolbar v-if="isEditForm" :recipe="recipe" />
          <RecipePageIngredientEditor v-if="isEditForm" :recipe="recipe" />
          <RecipePageScale :recipe="recipe" :scale.sync="scale" />

          <!--
            This section contains the 2 column layout for the recipe steps and other content.
          -->
          <v-row>
            <!--
              The left column is conditionally rendered based on cook mode.
            -->
            <v-col v-if="!isCookMode || isEditForm" cols="12" sm="12" md="4" lg="4">
              <RecipePageIngredientToolsView v-if="!isEditForm" :recipe="recipe" :scale="scale" />
              <RecipePageOrganizers v-if="$vuetify.breakpoint.mdAndUp" :recipe="recipe" @item-selected="chipClicked" />
            </v-col>
            <v-divider v-if="$vuetify.breakpoint.mdAndUp && !isCookMode" class="my-divider" :vertical="true" />

            <!--
              the right column is always rendered, but it's layout width is determined by where the left column is
              rendered.
            -->
            <v-col cols="12" sm="12" :md="8 + (isCookMode ? 1 : 0) * 4" :lg="8 + (isCookMode ? 1 : 0) * 4">
              <RecipePageInstructions
                v-model="recipe.recipeInstructions"
                :assets.sync="recipe.assets"
                :recipe="recipe"
                :scale="scale"
              />
              <div v-if="isEditForm" class="d-flex">
                <RecipeDialogBulkAdd class="ml-auto my-2 mr-1" @bulk-data="addStep" />
                <BaseButton class="my-2" @click="addStep()"> {{ $t("general.add") }}</BaseButton>
              </div>
              <div v-if="!$vuetify.breakpoint.mdAndUp">
                <RecipePageOrganizers :recipe="recipe" />
              </div>
              <RecipeNotes v-model="recipe.notes" :edit="isEditForm" />
            </v-col>
          </v-row>
          <RecipePageFooter :recipe="recipe" />
        </v-card-text>
      </v-card>
      <WakelockSwitch/>
      <RecipePageComments
        v-if="!recipe.settings.disableComments && !isEditForm && !isCookMode"
        :recipe="recipe"
        class="px-1 my-4 d-print-none"
      />
      <RecipePrintContainer :recipe="recipe" :scale="scale" />
    </v-container>
    <!-- Cook mode displayes two columns with ingredients and instructions side by side, each being scrolled individually, allowing to view both at the same timer -->
    <v-sheet v-show="isCookMode && !hasLinkedIngredients" key="cookmode" :style="{height: $vuetify.breakpoint.smAndUp ? 'calc(100vh - 48px)' : ''}"> <!-- the calc is to account for the toolbar a more dynamic solution could be needed  -->
      <v-row  style="height: 100%;"  no-gutters class="overflow-hidden">
        <v-col  cols="12" sm="5" class="overflow-y-auto pl-4 pr-3 py-2" style="height: 100%;">
          <div class="d-flex align-center">
            <RecipePageScale :recipe="recipe" :scale.sync="scale" />
          </div>
          <RecipePageIngredientToolsView v-if="!isEditForm" :recipe="recipe" :scale="scale" :is-cook-mode="isCookMode" />
          <v-divider></v-divider>
        </v-col>
        <v-col class="overflow-y-auto py-2" style="height: 100%;" cols="12" sm="7">
          <RecipePageInstructions
            v-model="recipe.recipeInstructions"
            class="overflow-y-hidden px-4"
            :assets.sync="recipe.assets"
            :recipe="recipe"
            :scale="scale"
          />
        </v-col>
      </v-row>

    </v-sheet>
    <v-sheet v-show="isCookMode && hasLinkedIngredients">
      <div class="mt-2 px-2 px-md-4">
        <RecipePageScale :recipe="recipe" :scale.sync="scale"/>
      </div>
      <RecipePageInstructions
        v-model="recipe.recipeInstructions"
        class="overflow-y-hidden mt-n5 px-2 px-md-4"
        :assets.sync="recipe.assets"
        :recipe="recipe"
        :scale="scale"
      />

      <div v-if="notLinkedIngredients.length > 0" class="px-2 px-md-4 pb-4 ">
        <v-divider></v-divider>
        <v-card flat>
          <v-card-title>{{ $t('recipe.not-linked-ingredients') }}</v-card-title>
            <RecipeIngredients
              :value="notLinkedIngredients"
              :scale="scale"
              :disable-amount="recipe.settings.disableAmount"
              :is-cook-mode="isCookMode">

            </RecipeIngredients>
        </v-card>
      </div>
    </v-sheet>
    <v-btn
      v-if="isCookMode"
      fab
      small
      color="primary"
      style="position: fixed; right: 12px; top: 60px;"
      @click="toggleCookMode()"
      >
      <v-icon>mdi-close</v-icon>
    </v-btn>
  </div>

</template>

<script lang="ts">
import {
  defineComponent,
  useContext,
  useRouter,
  computed,
  ref,
  onMounted,
  onUnmounted,
useRoute,
} from "@nuxtjs/composition-api";
import { invoke, until } from "@vueuse/core";
import RecipeIngredients from "../RecipeIngredients.vue";
import RecipePageEditorToolbar from "./RecipePageParts/RecipePageEditorToolbar.vue";
import RecipePageFooter from "./RecipePageParts/RecipePageFooter.vue";
import RecipePageHeader from "./RecipePageParts/RecipePageHeader.vue";
import RecipePageIngredientEditor from "./RecipePageParts/RecipePageIngredientEditor.vue";
import RecipePageIngredientToolsView from "./RecipePageParts/RecipePageIngredientToolsView.vue";
import RecipePageInstructions from "./RecipePageParts/RecipePageInstructions.vue";
import RecipePageOrganizers from "./RecipePageParts/RecipePageOrganizers.vue";
import RecipePageScale from "./RecipePageParts/RecipePageScale.vue";
import RecipePageInfoEditor from "./RecipePageParts/RecipePageInfoEditor.vue";
import RecipePageComments from "./RecipePageParts/RecipePageComments.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipePrintContainer from "~/components/Domain/Recipe/RecipePrintContainer.vue";
import {
  clearPageState,
  EditorMode,
  PageMode,
  usePageState,
  usePageUser,
} from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe, RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { useRouteQuery } from "~/composables/use-router";
import { useUserApi } from "~/composables/api";
import { uuid4, deepCopy } from "~/composables/use-utils";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";
import { useNavigationWarning } from "~/composables/use-navigation-warning";

const EDITOR_OPTIONS = {
  mode: "code",
  search: false,
  mainMenuBar: false,
};

export default defineComponent({
  components: {
    RecipePageHeader,
    RecipePrintContainer,
    RecipePageComments,
    RecipePageInfoEditor,
    RecipePageEditorToolbar,
    RecipePageIngredientEditor,
    RecipePageOrganizers,
    RecipePageScale,
    RecipePageIngredientToolsView,
    RecipeDialogBulkAdd,
    RecipeNotes,
    RecipePageInstructions,
    RecipePageFooter,
    RecipeIngredients,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { $auth } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const { isOwnGroup } = useLoggedInState();

    const router = useRouter();
    const api = useUserApi();
    const { pageMode, editMode, setMode, isEditForm, isEditJSON, isCookMode, isEditMode, toggleCookMode } =
      usePageState(props.recipe.slug);
    const { deactivateNavigationWarning } = useNavigationWarning();
    const notLinkedIngredients = computed(() => {
      return props.recipe.recipeIngredient.filter((ingredient) => {
        return !props.recipe.recipeInstructions.some((step) => step.ingredientReferences?.map((ref) => ref.referenceId).includes(ingredient.referenceId));
      })
    })

    /** =============================================================
     * Recipe Snapshot on Mount
     * this is used to determine if the recipe has been changed since the last save
     * and prompts the user to save if they have unsaved changes.
     */
    const originalRecipe = ref<Recipe | null>(null);

    invoke(async () => {
      await until(props.recipe).not.toBeNull();
      originalRecipe.value = deepCopy(props.recipe);
    });

    onUnmounted(async () => {
      const isSame = JSON.stringify(props.recipe) === JSON.stringify(originalRecipe.value);
      if (isEditMode.value && !isSame && props.recipe?.slug !== undefined) {
        const save = window.confirm(
          i18n.tc("general.unsaved-changes"),
          );

        if (save) {
          await api.recipes.updateOne(props.recipe.slug, props.recipe);
        }
      }
      deactivateNavigationWarning();
      toggleCookMode()

      clearPageState(props.recipe.slug || "");
      console.debug("reset RecipePage state during unmount");
    });
    const hasLinkedIngredients = computed(() => {
      return props.recipe.recipeInstructions.some((step) => step.ingredientReferences && step.ingredientReferences.length > 0);
    })
    /** =============================================================
     * Set State onMounted
     */

    type BooleanString = "true" | "false" | "";

    const edit = useRouteQuery<BooleanString>("edit", "");

    onMounted(() => {
      if (edit.value === "true") {
        setMode(PageMode.EDIT);
      }
    });

    /** =============================================================
     * Recipe Save Delete
     */

    async function saveRecipe() {
      const { data } = await api.recipes.updateOne(props.recipe.slug, props.recipe);
      setMode(PageMode.VIEW);
      if (data?.slug) {
        router.push(`/g/${groupSlug.value}/r/` + data.slug);
      }
    }

    async function deleteRecipe() {
      const { data } = await api.recipes.deleteOne(props.recipe.slug);
      if (data?.slug) {
        router.push(`/g/${groupSlug.value}`);
      }
    }

    /** =============================================================
     * View Preferences
     */
    const { $vuetify, i18n } = useContext();

    const landscape = computed(() => {
      const preferLandscape = props.recipe.settings.landscapeView;
      const smallScreen = !$vuetify.breakpoint.smAndUp;

      if (preferLandscape) {
        return true;
      } else if (smallScreen) {
        return true;
      }

      return false;
    });

    /** =============================================================
     * Bulk Step Editor
     * TODO: Move to RecipePageInstructions component
     */

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

    /** =============================================================
     * Meta Tags
     */
    const { user } = usePageUser();

    /** =============================================================
     * RecipeChip Clicked
     */

    function chipClicked(item: RecipeTag | RecipeCategory | RecipeTool, itemType: string) {
      if (!item.id) {
        return;
      }
      router.push(`/g/${groupSlug.value}?${itemType}=${item.id}`);
    }

    return {
      user,
      isOwnGroup,
      api,
      scale: ref(1),
      EDITOR_OPTIONS,
      landscape,

      pageMode,
      editMode,
      PageMode,
      EditorMode,
      isEditMode,
      isEditForm,
      isEditJSON,
      isCookMode,
      toggleCookMode,
      saveRecipe,
      deleteRecipe,
      addStep,
      hasLinkedIngredients,
      notLinkedIngredients,
      chipClicked,
    };
  },
  head: {},
});
</script>

<style lang="css">
.flip-list-move {
  transition: transform 0.5s;
}
.no-move {
  transition: transform 0s;
}
.ghost {
  opacity: 0.5;
}
.list-group {
  min-height: 38px;
}
.list-group-item i {
  cursor: pointer;
}
</style>
