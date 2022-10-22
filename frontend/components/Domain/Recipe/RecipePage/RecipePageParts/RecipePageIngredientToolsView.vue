<template>
  <div>
    <RecipeIngredients
      :value="recipe.recipeIngredient"
      :scale="scale"
      :disable-amount="recipe.settings.disableAmount"
    />
    <div v-if="!isEditMode && recipe.tools && recipe.tools.length > 0">
      <h2 class="mb-2 mt-4">Required Tools</h2>
      <v-list-item v-for="(tool, index) in recipe.tools" :key="index" dense>
        <v-checkbox
          v-model="recipe.tools[index].onHand"
          hide-details
          class="pt-0 my-auto py-auto"
          color="secondary"
          @change="updateTool(index)"
        >
        </v-checkbox>
        <v-list-item-content>
          {{ tool.name }}
        </v-list-item-content>
      </v-list-item>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { useToolStore } from "~/composables/store";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";

export default defineComponent({
  components: {
    RecipeIngredients,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    scale: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const toolStore = useToolStore();
    const { user } = usePageUser();
    const { isEditMode } = usePageState(props.recipe.slug);

    function updateTool(index: number) {
      if (user.id) {
        toolStore.actions.updateOne(props.recipe.tools[index]);
      } else {
        console.log("no user, skipping server update");
      }
    }

    return {
      toolStore,
      isEditMode,
      updateTool,
    };
  },
});
</script>
