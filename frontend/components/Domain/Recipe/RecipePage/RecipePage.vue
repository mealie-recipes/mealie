<template>
  <v-container :class="{ 'pa-0': $vuetify.breakpoint.smAndDown }">
    <v-card :flat="$vuetify.breakpoint.smAndDown" class="d-print-none">
      <RecipePageHeader :recipe="recipe" :landscape="landscape" @save="saveRecipe" @delete="deleteRecipe" />
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
        <RecipePageEditorToolbar v-if="isEditForm" :recipe="recipe" />
        <RecipePageTitleContent :recipe="recipe" :landscape="landscape" />
        <RecipePageIngredientEditor v-if="isEditForm" :recipe="recipe" />
        <RecipePageScale :recipe="recipe" :scale.sync="scale" :landscape="landscape" />

        <!--
          This section contains the 2 column layout for the recipe steps and other content.
         -->
        <v-row>
          <!--
            The left column is conditionally rendered based on cook mode.
           -->
          <v-col v-if="!isCookMode || isEditForm" cols="12" sm="12" md="4" lg="4">
            <RecipePageIngredientToolsView v-if="!isEditForm" :recipe="recipe" :scale="scale" />
            <RecipePageOrganizers v-if="$vuetify.breakpoint.mdAndUp" :recipe="recipe" />
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
              <BaseButton class="my-2" @click="addStep()"> {{ $t("general.new") }}</BaseButton>
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

    <div
      v-if="recipe && wakeIsSupported"
      class="d-print-none d-flex px-2"
      :class="$vuetify.breakpoint.smAndDown ? 'justify-center' : 'justify-end'"
    >
      <v-switch v-model="wakeLock" small label="Keep Screen Awake" />
    </div>

    <RecipePageComments
      v-if="user.id && !recipe.settings.disableComments && !isEditForm && !isCookMode"
      :recipe="recipe"
      class="px-1 my-4 d-print-none"
    />
    <RecipePrintView :recipe="recipe" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useContext, useRouter, computed, ref, useMeta } from "@nuxtjs/composition-api";
import { invoke, until, useWakeLock } from "@vueuse/core";
import { onMounted, onUnmounted } from "vue-demi";
import RecipePageEditorToolbar from "./RecipePageParts/RecipePageEditorToolbar.vue";
import RecipePageFooter from "./RecipePageParts/RecipePageFooter.vue";
import RecipePageHeader from "./RecipePageParts/RecipePageHeader.vue";
import RecipePageIngredientEditor from "./RecipePageParts/RecipePageIngredientEditor.vue";
import RecipePageIngredientToolsView from "./RecipePageParts/RecipePageIngredientToolsView.vue";
import RecipePageInstructions from "./RecipePageParts/RecipePageInstructions.vue";
import RecipePageOrganizers from "./RecipePageParts/RecipePageOrganizers.vue";
import RecipePageScale from "./RecipePageParts/RecipePageScale.vue";
import RecipePageTitleContent from "./RecipePageParts/RecipePageTitleContent.vue";
import RecipePageComments from "./RecipePageParts/RecipePageComments.vue";
import RecipePrintView from "~/components/Domain/Recipe/RecipePrintView.vue";
import { EditorMode, PageMode, usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { useRecipeMeta } from "~/composables/recipes";
import { useRouteQuery } from "~/composables/use-router";
import { useUserApi } from "~/composables/api";
import { uuid4, deepCopy } from "~/composables/use-utils";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeNotes from "~/components/Domain/Recipe/RecipeNotes.vue";

const EDITOR_OPTIONS = {
  mode: "code",
  search: false,
  mainMenuBar: false,
};

export default defineComponent({
  components: {
    RecipePageHeader,
    RecipePrintView,
    RecipePageComments,
    RecipePageTitleContent,
    RecipePageEditorToolbar,
    RecipePageIngredientEditor,
    RecipePageOrganizers,
    RecipePageScale,
    RecipePageIngredientToolsView,
    RecipeDialogBulkAdd,
    RecipeNotes,
    RecipePageInstructions,
    RecipePageFooter,
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
    const { pageMode, editMode, setMode, isEditForm, isEditJSON, isCookMode, isEditMode, toggleCookMode } =
      usePageState(props.recipe.slug);

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
          "You have unsaved changes. Do you want to save before leaving?\n\nOkay to save, Cancel to discard changes."
        );

        if (save) {
          await api.recipes.updateOne(props.recipe.slug, props.recipe);
        }
      }
    });

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
     * Wake Lock
     */

    const { isSupported: wakeIsSupported, isActive, request, release } = useWakeLock();

    const wakeLock = computed({
      get: () => isActive,
      set: () => {
        if (isActive.value) {
          unlockScreen();
        } else {
          lockScreen();
        }
      },
    });

    async function lockScreen() {
      if (wakeIsSupported) {
        console.log("Wake Lock Requested");
        await request("screen");
      }
    }

    async function unlockScreen() {
      if (wakeIsSupported || isActive) {
        console.log("Wake Lock Released");
        await release();
      }
    }

    onMounted(() => lockScreen());
    onUnmounted(() => unlockScreen());

    /** =============================================================
     * Recipe Save Delete
     */

    async function saveRecipe() {
      const { data } = await api.recipes.updateOne(props.recipe.slug, props.recipe);
      setMode(PageMode.VIEW);
      if (data?.slug) {
        router.push("/recipe/" + data.slug);
      }
    }

    async function deleteRecipe() {
      const { data } = await api.recipes.deleteOne(props.recipe.slug);
      if (data?.slug) {
        router.push("/");
      }
    }

    /** =============================================================
     * View Preferences
     */
    const { $vuetify } = useContext();

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
    const { recipeMeta } = useRecipeMeta();
    useMeta(recipeMeta(ref(props.recipe)));

    const { user } = usePageUser();

    return {
      user,
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

      wakeLock,
      wakeIsSupported,
      saveRecipe,
      deleteRecipe,
      addStep,
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
.list-group-item {
  cursor: move;
}
.list-group-item i {
  cursor: pointer;
}
</style>
