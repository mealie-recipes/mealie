<template>
  <div>
    <RecipeIngredients
      :value="recipe.recipeIngredient"
      :scale="scale"
      :is-cook-mode="isCookMode"
    />
    <div v-if="!isEditMode && recipe.tools && recipe.tools.length > 0">
      <h2 class="mt-4 text-h5 font-weight-medium opacity-80">
        {{ $t('tool.required-tools') }}
      </h2>
      <v-list density="compact">
        <v-list-item
          v-for="(tool, index) in recipe.tools"
          :key="index"
          density="compact"
          class="px-1"
        >
          <template #prepend>
            <v-checkbox
              v-model="recipeTools[index].onHand"
              hide-details
              class="pt-0 py-auto"
              color="secondary"
              density="compact"
              @change="updateTool(index)"
            />
          </template>
          <v-list-item-title>
            {{ tool.name }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { useToolStore } from "~/composables/store";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeTool } from "~/lib/api/types/recipe";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

interface Props {
  recipe: NoUndefinedField<Recipe>;
  scale: number;
  isCookMode?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  isCookMode: false,
});

const { isOwnGroup } = useLoggedInState();

const toolStore = isOwnGroup.value ? useToolStore() : null;
const { user } = usePageUser();
const { isEditMode } = usePageState(props.recipe.slug);

const recipeTools = computed(() => {
  if (!(user.householdSlug && toolStore)) {
    return props.recipe.tools.map(tool => ({ ...tool, onHand: false }) as RecipeToolWithOnHand);
  }
  else {
    return props.recipe.tools.map((tool) => {
      const onHand = tool.householdsWithTool?.includes(user.householdSlug) || false;
      return { ...tool, onHand } as RecipeToolWithOnHand;
    });
  }
});

function updateTool(index: number) {
  if (user.id && user.householdSlug && toolStore) {
    const tool = recipeTools.value[index];
    if (tool.onHand && !tool.householdsWithTool?.includes(user.householdSlug)) {
      if (!tool.householdsWithTool) {
        tool.householdsWithTool = [user.householdSlug];
      }
      else {
        tool.householdsWithTool.push(user.householdSlug);
      }
    }
    else if (!tool.onHand && tool.householdsWithTool?.includes(user.householdSlug)) {
      tool.householdsWithTool = tool.householdsWithTool.filter(household => household !== user.householdSlug);
    }

    toolStore.actions.updateOne(tool);
  }
  else {
    console.log("no user, skipping server update");
  }
}
</script>
