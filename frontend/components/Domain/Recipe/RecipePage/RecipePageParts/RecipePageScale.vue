<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <v-tooltip v-if="!isEditMode && recipe.recipeYield" small top color="secondary darken-1">
      <template #activator="{ on, attrs }">
        <RecipeScaleEditButton
          v-model.number="scaleValue"
          v-bind="attrs"
          :recipe-yield="recipe.recipeYield"
          :basic-yield="basicYield"
          :scaled-yield="scaledYield"
          :edit-scale="!recipe.settings.disableAmount && !isEditMode"
          v-on="on"
        />
      </template>
      <span> {{ $t("recipe.edit-scale") }} </span>
    </v-tooltip>
    <v-spacer></v-spacer>

    <RecipeRating
      v-if="landscape && $vuetify.breakpoint.smAndUp"
      :key="recipe.slug"
      v-model="recipe.rating"
      :recipe-id="recipe.id"
      :slug="recipe.slug"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { useExtractRecipeYield } from "~/composables/recipe-page/use-extract-recipe-yield";

export default defineComponent({
  components: {
    RecipeScaleEditButton,
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
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props, { emit }) {
    const { isEditMode } = usePageState(props.recipe.slug);

    const scaleValue = computed<number>({
      get() {
        return props.scale;
      },
      set(val) {
        emit("update:scale", val);
      },
    });

    const scaledYield = computed(() => {
      return useExtractRecipeYield(props.recipe.recipeYield, scaleValue.value);
    });

    const basicYield = computed(() => {
      return useExtractRecipeYield(props.recipe.recipeYield, 1);
    });

    return {
      scaleValue,
      basicYield,
      scaledYield,
      isEditMode,
    };
  },
});
</script>
