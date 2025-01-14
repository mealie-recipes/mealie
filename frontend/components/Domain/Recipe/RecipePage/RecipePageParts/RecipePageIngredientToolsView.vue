<template>
  <div>
    <RecipeIngredients
      :value="recipe.recipeIngredient"
      :scale="scale"
      :disable-amount="recipe.settings.disableAmount"
      :is-cook-mode="isCookMode"
    />
    <div v-if="!isEditMode && recipe.tools && recipe.tools.length > 0">
      <h2 class="mb-2 mt-4">{{ $t('tool.required-tools') }}</h2>
      <v-list-item v-for="(tool, index) in recipe.tools" :key="index" dense>
        <v-checkbox
          v-model="recipeTools[index].onHand"
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
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { useToolStore } from "~/composables/store";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe, RecipeTool } from "~/lib/api/types/recipe";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

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
    isCookMode: {
      type: Boolean,
      default: false,
    }
  },
  setup(props) {
    const { isOwnGroup } = useLoggedInState();

    const toolStore = isOwnGroup.value ? useToolStore() : null;
    const { user } = usePageUser();
    const { isEditMode } = usePageState(props.recipe.slug);

    const recipeTools = computed(() => {
      if (!(user.householdSlug && toolStore)) {
        return props.recipe.tools.map((tool) => ({ ...tool, onHand: false }) as RecipeToolWithOnHand);
      } else {
        return props.recipe.tools.map((tool) => {
          const onHand = tool.householdsWithTool?.includes(user.householdSlug) || false;
          return { ...tool, onHand } as RecipeToolWithOnHand;
        });
      }
    })

    function updateTool(index: number) {
      if (user.id && user.householdSlug && toolStore) {
        const tool = recipeTools.value[index];
        if (tool.onHand && !tool.householdsWithTool?.includes(user.householdSlug)) {
          if (!tool.householdsWithTool) {
            tool.householdsWithTool = [user.householdSlug];
          } else {
            tool.householdsWithTool.push(user.householdSlug);
          }
        } else if (!tool.onHand && tool.householdsWithTool?.includes(user.householdSlug)) {
          tool.householdsWithTool = tool.householdsWithTool.filter((household) => household !== user.householdSlug);
        }

        toolStore.actions.updateOne(tool);
      } else {
        console.log("no user, skipping server update");
      }
    }

    return {
      toolStore,
      recipeTools,
      isEditMode,
      updateTool,
    };
  },
});
</script>
