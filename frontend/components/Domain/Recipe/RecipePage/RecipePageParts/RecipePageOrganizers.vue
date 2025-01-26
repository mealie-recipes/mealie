<template>
  <div>
    <!-- Recipe Categories -->
    <v-card v-if="recipe.recipeCategory.length > 0 || isEditForm" :class="{'mt-10': !isEditForm}">
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
        <RecipeChips v-else :items="recipe.recipeCategory" v-on="$listeners" />
      </v-card-text>
    </v-card>

    <!-- Recipe Tags -->
    <v-card v-if="recipe.tags.length > 0 || isEditForm" class="mt-4">
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
        <RecipeChips v-else :items="recipe.tags" url-prefix="tags" v-on="$listeners" />
      </v-card-text>
    </v-card>

    <!-- Recipe Tools Edit -->
    <v-card v-if="isEditForm" class="mt-2">
      <v-card-title class="py-2"> {{ $t('tool.required-tools') }} </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text class="pt-0">
        <RecipeOrganizerSelector v-model="recipe.tools" selector-type="tools" v-on="$listeners" />
      </v-card-text>
    </v-card>

    <RecipeNutrition v-if="recipe.settings.showNutrition" v-model="recipe.nutrition" class="mt-4" :edit="isEditForm" />
    <RecipeAssets
      v-if="recipe.settings.showAssets"
      v-model="recipe.assets"
      :edit="isEditForm"
      :slug="recipe.slug"
      :recipe-id="recipe.id"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import RecipeOrganizerSelector from "@/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeChips from "@/components/Domain/Recipe/RecipeChips.vue";
import RecipeAssets from "@/components/Domain/Recipe/RecipeAssets.vue";
export default defineComponent({
  components: {
    RecipeOrganizerSelector,
    RecipeNutrition,
    RecipeChips,
    RecipeAssets,
  },
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { user } = usePageUser();
    const { isEditForm } = usePageState(props.recipe.slug);



    return {
      isEditForm,
      user,
    };
  },
});
</script>
