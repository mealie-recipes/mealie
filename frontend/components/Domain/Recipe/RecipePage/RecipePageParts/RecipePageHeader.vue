<template>
  <div>
    <RecipePageInfoCard :recipe="recipe" :recipe-scale="recipeScale" :landscape="landscape" />
    <v-divider />
    <RecipeActionMenu
      :recipe="recipe"
      :slug="recipe.slug"
      :recipe-scale="recipeScale"
      :can-edit="canEditRecipe"
      :name="recipe.name"
      :logged-in="isOwnGroup"
      :open="isEditMode"
      :recipe-id="recipe.id"
      class="ml-auto mt-n2 pb-4"
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
import RecipePageInfoCard from "~/components/Domain/Recipe/RecipePage/RecipePageParts/RecipePageInfoCard.vue";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import { useStaticRoutes, useUserApi  } from "~/composables/api";
import { HouseholdSummary } from "~/lib/api/types/household";
import { Recipe } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { usePageState, usePageUser, PageMode, EditorMode } from "~/composables/recipe-page/shared-state";
export default defineComponent({
  components: {
    RecipePageInfoCard,
    RecipeActionMenu,
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

    const recipeHousehold = ref<HouseholdSummary>();
    if (user) {
      const userApi = useUserApi();
      userApi.households.getOne(props.recipe.householdId).then(({ data }) => {
        recipeHousehold.value = data || undefined;
      });
    }
    const { canEditRecipe } = useRecipePermissions(props.recipe, recipeHousehold, user);

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
