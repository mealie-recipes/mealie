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
      </v-card-text>
    </v-card>

    <RecipeComments
      v-if="!recipe.settings.disableComments && !isEditForm && !isCookMode"
      v-model="recipe.comments"
      :slug="recipe.slug"
      :recipe-id="recipe.id"
      class="px-1 my-4 d-print-none"
    />
    <RecipePrintView :recipe="recipe" />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useContext, useRouter, computed, ref } from "@nuxtjs/composition-api";
import { Parts } from "./RecipePageParts/parts";
import { EditorMode, PageMode, usePageState } from "~/composables/recipe-page/shared-state";
import { Recipe } from "~/types/api-types/recipe";
import { NoUndefinedField } from "~/types/api";
import { useUserApi } from "~/composables/api";
import { uuid4 } from "~/composables/use-utils";

const EDITOR_OPTIONS = {
  mode: "code",
  search: false,
  mainMenuBar: false,
};

export default defineComponent({
  components: Parts,
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const router = useRouter();
    const api = useUserApi();
    const { pageMode, editMode, setMode, isEditForm, isEditJSON, isCookMode, toggleCookMode } = usePageState(
      props.recipe.slug
    );

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

    const scale = ref(1);

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

    return {
      EDITOR_OPTIONS,
      landscape,
      scale,

      // Page Mode Settings
      pageMode,
      editMode,
      PageMode,
      EditorMode,
      isEditForm,
      isEditJSON,
      isCookMode,
      toggleCookMode,

      // CRUD Methods
      saveRecipe,
      deleteRecipe,
      addStep,
    };
  },
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
