<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <RecipeScaleEditButton
      v-if="!isEditMode"
      v-model.number="scaleValue"
      :recipe-servings="recipeServings"
      :edit-scale="!recipe.settings.disableAmount && !isEditMode"
    />
  </div>
</template>

<script lang="ts">
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";
import { usePageState } from "~/composables/recipe-page/shared-state";

export default defineNuxtComponent({
  components: {
    RecipeScaleEditButton,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },
  emits: ["update:scale"],
  setup(props, { emit }) {
    const { isEditMode } = usePageState(props.recipe.slug);

    const recipeServings = computed<number>(() => {
      return props.recipe.recipeServings || props.recipe.recipeYieldQuantity || 1;
    });

    const scaleValue = computed<number>({
      get() {
        return props.scale;
      },
      set(val) {
        emit("update:scale", val);
      },
    });

    return {
      recipeServings,
      scaleValue,
      isEditMode,
    };
  },
});
</script>
