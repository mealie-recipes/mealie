<template>
  <div>
    <div class="d-flex justify-end flex-wrap align-stretch">
      <v-card v-if="!landscape" width="50%" flat class="d-flex flex-column justify-center align-center">
        <v-card-text>
          <v-card-title class="headline pa-0 flex-column align-center">
            {{ recipe.name }}
            <RecipeRating :key="recipe.slug" :value="recipe.rating" :name="recipe.name" :slug="recipe.slug" />
          </v-card-title>
          <v-divider class="my-2"></v-divider>
          <SafeMarkdown :source="recipe.description" />
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
      v-if="user.id"
      :recipe="recipe"
      :slug="recipe.slug"
      :locked="user.id !== recipe.userId && recipe.settings.locked"
      :name="recipe.name"
      :logged-in="$auth.loggedIn"
      :open="isEditMode"
      :recipe-id="recipe.id"
      :show-ocr-button="recipe.isOcrRecipe"
      class="ml-auto mt-n8 pb-4"
      @close="setMode(PageMode.VIEW)"
      @json="toggleEditMode()"
      @edit="setMode(PageMode.EDIT)"
      @save="$emit('save')"
      @delete="$emit('delete')"
      @print="printRecipe"
      @ocr="goToOcrEditor"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext, computed, ref, watch, useRouter } from "@nuxtjs/composition-api";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
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
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    landscape: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { recipeImage } = useStaticRoutes();
    const { imageKey, pageMode, editMode, setMode, toggleEditMode, isEditMode } = usePageState(props.recipe.slug);
    const { user } = usePageUser();
    const router = useRouter();

    function printRecipe() {
      window.print();
    }

    const { $vuetify } = useContext();

    const hideImage = ref(false);
    const imageHeight = computed(() => {
      return $vuetify.breakpoint.xs ? "200" : "400";
    });

    const recipeImageUrl = computed(() => {
      return recipeImage(props.recipe.id, props.recipe.image, imageKey.value);
    });

    function goToOcrEditor() {
      router.push("/recipe/" + props.recipe.slug + "/ocr-editor");
    }

    watch(
      () => recipeImageUrl.value,
      () => {
        hideImage.value = false;
      }
    );

    return {
      setMode,
      toggleEditMode,
      recipeImage,
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
      goToOcrEditor,
    };
  },
});
</script>
