<template>
  <div>
    <div class="d-flex justify-end flex-wrap align-stretch">
      <v-card v-if="!landscape" width="50%" flat class="d-flex flex-column justify-center align-center">
        <v-card-text>
          <v-card-title class="headline pa-0 flex-column align-center">
            {{ recipe.name }}
            <RecipeRating :key="recipe.slug" :value="recipe.rating" :recipe-id="recipe.id" :slug="recipe.slug" />
          </v-card-title>
          <v-divider class="my-2"></v-divider>
          <SafeMarkdown :source="recipe.description" />
          <v-divider></v-divider>
          <div v-if="isOwnGroup" class="d-flex justify-center mt-5">
            <RecipeLastMade
              v-model="recipe.lastMade"
              :recipe="recipe"
              class="d-flex justify-center flex-wrap"
              :class="true ? undefined : 'force-bottom'"
            />
          </div>
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
        :max-width="landscape ? null : '50%'"
        min-height="50"
        :height="hideImage ? undefined : imageHeight"
        :src="recipeImageUrl"
        class="d-print-none"
        @error="hideImage = true"
      >
      </v-img>
    </div>
    <v-divider></v-divider>
    <RecipeActionMenu
      :recipe="recipe"
      :slug="recipe.slug"
      :recipe-scale="recipeScale"
      :can-edit="canEditRecipe"
      :name="recipe.name"
      :logged-in="isOwnGroup"
      :open="isEditMode"
      :recipe-id="recipe.id"
      class="ml-auto mt-n8 pb-4"
      @close="setMode(PageMode.VIEW)"
      @json="toggleEditMode()"
      @edit="setMode(PageMode.EDIT)"
      @save="$emit('save')"
      @delete="$emit('delete')"
      @print="printRecipe"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext, computed, ref, watch } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useRecipePermissions } from "~/composables/recipes";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeLastMade from "~/components/Domain/Recipe/RecipeLastMade.vue";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import { useStaticRoutes } from "~/composables/api";
import { Recipe } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { usePageState, usePageUser, PageMode, EditorMode } from "~/composables/recipe-page/shared-state";
export default defineComponent({
  components: {
    RecipeTimeCard,
    RecipeActionMenu,
    RecipeRating,
    RecipeLastMade,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    recipeScale: {
      type: Number,
      default: 1,
    },
    landscape: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { $vuetify } = useContext();
    const { recipeImage } = useStaticRoutes();
    const { imageKey, pageMode, editMode, setMode, toggleEditMode, isEditMode } = usePageState(props.recipe.slug);
    const { user } = usePageUser();
    const { isOwnGroup } = useLoggedInState();
    const { canEditRecipe } = useRecipePermissions(props.recipe, user);

    function printRecipe() {
      window.print();
    }

    const hideImage = ref(false);
    const imageHeight = computed(() => {
      return $vuetify.breakpoint.xs ? "200" : "400";
    });

    const recipeImageUrl = computed(() => {
      return recipeImage(props.recipe.id, props.recipe.image, imageKey.value);
    });

    watch(
      () => recipeImageUrl.value,
      () => {
        hideImage.value = false;
      }
    );

    return {
      isOwnGroup,
      setMode,
      toggleEditMode,
      recipeImage,
      canEditRecipe,
      imageKey,
      user,
      PageMode,
      pageMode,
      EditorMode,
      editMode,
      printRecipe,
      imageHeight,
      hideImage,
      isEditMode,
      recipeImageUrl,
    };
  },
});
</script>
