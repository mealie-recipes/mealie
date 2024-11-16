<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <v-tooltip v-if="!isEditMode" small top color="secondary darken-1">
      <template #activator="{ on, attrs }">
        <RecipeScaleEditButton
          v-model.number="scaleValue"
          v-bind="attrs"
          :recipe-servings="recipeServings"
          :edit-scale="!recipe.settings.disableAmount && !isEditMode"
          v-on="on"
        />
      </template>
      <span> {{ $t("recipe.edit-scale") }} </span>
    </v-tooltip>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { usePageState } from "~/composables/recipe-page/shared-state";

export default defineComponent({
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
