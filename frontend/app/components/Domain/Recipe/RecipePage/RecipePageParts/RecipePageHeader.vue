<template>
  <div>
    <RecipePageInfoCard
      :recipe="recipe"
      :recipe-scale="recipeScale"
      :landscape="landscape"
    />
    <v-divider />
    <RecipeActionMenu
      :recipe="recipe"
      :slug="recipe.slug"
      :recipe-scale="recipeScale"
      :can-edit="canEditRecipe && !photosBusy"
      :name="recipe.name"
      :logged-in="isOwnGroup"
      :open="isEditMode"
      :recipe-id="recipe.id"
      class="ml-auto mt-n7 pb-4"
      @close="$emit('close')"
      @json="toggleEditMode()"
      @edit="setMode(PageMode.EDIT)"
      @save="$emit('save')"
      @delete="$emit('delete')"
      @print="printRecipe"
    />
    <RecipePhotos
      v-if="!isEditMode"
      v-model="recipe"
      :can-edit="canEditRecipe"
      @busy="photosBusy = $event"
      @saved="$emit('photos-saved')"
    />
  </div>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useRecipePermissions } from "~/composables/recipes";
import RecipePageInfoCard from "~/components/Domain/Recipe/RecipePage/RecipePageParts/RecipePageInfoCard.vue";
import RecipeActionMenu from "~/components/Domain/Recipe/RecipeActionMenu.vue";
import RecipePhotos from "~/components/Domain/Recipe/RecipePhotos.vue";
import { useStaticRoutes, useUserApi } from "~/composables/api";
import type { HouseholdSummary } from "~/lib/api/types/household";
import type { RecipeOut } from "~/lib/api/types/recipe";
import { usePageState, usePageUser, PageMode } from "~/composables/recipe-page/shared-state";

interface Props {
  recipeScale?: number;
  landscape?: boolean;
}
withDefaults(defineProps<Props>(), {
  recipeScale: 1,
  landscape: false,
});

defineEmits(["save", "delete", "print", "close", "photos-saved"]);
const recipe = defineModel<RecipeOut>({ required: true });
const photosBusy = ref(false);

const { recipeImage } = useStaticRoutes();
const { imageKey, setMode, toggleEditMode, isEditMode } = usePageState(recipe.value.slug);
const { user } = usePageUser();
const { isOwnGroup } = useLoggedInState();

const recipeHousehold = ref<HouseholdSummary>();
if (user) {
  const userApi = useUserApi();
  userApi.households.getOne(recipe.value.householdId).then(({ data }) => {
    recipeHousehold.value = data || undefined;
  });
}
const { canEditRecipe } = useRecipePermissions(recipe.value, recipeHousehold, user);

function printRecipe() {
  window.print();
}

const hideImage = ref(false);

const recipeImageUrl = computed(() => {
  return recipeImage(recipe.value.id, recipe.value.image, imageKey.value);
});

watch(
  () => recipeImageUrl.value,
  () => {
    hideImage.value = false;
  },
);
</script>
