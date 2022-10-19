<template>
  <div class="d-flex justify-start align-center">
    <RecipeImageUploadBtn class="my-1" :slug="recipe.slug" @upload="uploadImage" @refresh="imageKey++" />
    <RecipeSettingsMenu
      class="my-1 mx-1"
      :value="recipe.settings"
      :is-owner="recipe.userId == user.id"
      @upload="uploadImage"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, onUnmounted } from "@nuxtjs/composition-api";
import { clearPageState, usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import RecipeImageUploadBtn from "~/components/Domain/Recipe/RecipeImageUploadBtn.vue";
import RecipeSettingsMenu from "~/components/Domain/Recipe/RecipeSettingsMenu.vue";

export default defineComponent({
  components: {
    RecipeImageUploadBtn,
    RecipeSettingsMenu,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { user } = usePageUser();
    const api = useUserApi();
    const { imageKey } = usePageState(props.recipe.slug);
    onUnmounted(() => {
      clearPageState(props.recipe.slug);
      console.debug("reset RecipePage state during unmount");
    });
    async function uploadImage(fileObject: File) {
      if (!props.recipe || !props.recipe.slug) {
        return;
      }
      const newVersion = await api.recipes.updateImage(props.recipe.slug, fileObject);
      if (newVersion?.data?.image) {
        props.recipe.image = newVersion.data.image;
      }
      imageKey.value++;
    }

    return {
      user,
      uploadImage,
      imageKey,
    };
  },
});
</script>
