<template>
  <div>
    <!-- Recipe Categories -->
    <v-card
      v-if="recipe.recipeCategory.length > 0 || isEditForm"
      :class="{ 'mt-10': !isEditForm }"
    >
      <v-card-title class="py-2">
        {{ $t("recipe.categories") }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-if="isEditForm"
          v-model="recipe.recipeCategory"
          :return-object="true"
          :show-add="true"
          selector-type="categories"
        />
        <RecipeChips
          v-else
          :items="recipe.recipeCategory"
          v-bind="$attrs"
        />
      </v-card-text>
    </v-card>

    <!-- Recipe Tags -->
    <v-card
      v-if="recipe.tags.length > 0 || isEditForm"
      class="mt-4"
    >
      <v-card-title class="py-2">
        {{ $t("tag.tags") }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-if="isEditForm"
          v-model="recipe.tags"
          :return-object="true"
          :show-add="true"
          selector-type="tags"
        />
        <RecipeChips
          v-else
          :items="recipe.tags"
          url-prefix="tags"
          v-bind="$attrs"
        />
      </v-card-text>
    </v-card>

    <!-- Recipe Tools Edit -->
    <v-card
      v-if="isEditForm"
      class="mt-2"
    >
      <v-card-title class="py-2">
        {{ $t('tool.required-tools') }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-model="recipe.tools"
          selector-type="tools"
          v-bind="$attrs"
        />
      </v-card-text>
    </v-card>

    <RecipeNutrition
      v-if="recipe.settings.showNutrition"
      v-model="recipe.nutrition"
      class="mt-4"
      :edit="isEditForm"
      :loading="parserLoading"
      @fetch-nutrition-info="fetchNutritionInfo"
    />
    <RecipeAssets
      v-if="recipe.settings.showAssets"
      v-model="recipe.assets"
      :edit="isEditForm"
      :slug="recipe.slug"
      :recipe-id="recipe.id"
    />
  </div>
</template>

<script lang="ts" setup>
import { usePageState } from "~/composables/recipe-page/shared-state";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";
import RecipeOrganizerSelector from "@/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeChips from "@/components/Domain/Recipe/RecipeChips.vue";
import RecipeAssets from "@/components/Domain/Recipe/RecipeAssets.vue";
import { useUserApi } from "~/composables/api/api-client";
import { parseIngredientText } from "~/composables/recipes";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
const { isEditForm } = usePageState(recipe.value.slug);

const userApi = useUserApi();

const ingredientCopyText = computed(() => {
  const components: string[] = [];
  if (recipe.value.recipeIngredient) {
    recipe.value.recipeIngredient.forEach((ingredient) => {
      if (ingredient.title) {
        if (components.length) {
          components.push("");
        }

        components.push(`[${ingredient.title}]`);
      }

      components.push(parseIngredientText(ingredient, 1, false));
    });
  }
  return components.join("\n");
});

const parserLoading = ref(false);

async function fetchNutritionInfo() {
  parserLoading.value = true;
  const fetchString = "Number of servings: " + (recipe.value.recipeServings || recipe.value.recipeYieldQuantity || 1) + "\n\n" + ingredientCopyText.value;
  const data = await userApi.recipes.fetchNutrition(fetchString);
  if (data.data) {
    recipe.value.nutrition = data.data;
  }
  parserLoading.value = false;
}
</script>
