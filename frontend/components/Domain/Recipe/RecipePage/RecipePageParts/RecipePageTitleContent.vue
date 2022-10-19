<template>
  <div>
    <template v-if="!isEditMode && landscape">
      <v-card-title class="px-0 py-2 ma-0 headline">
        {{ recipe.name }}
      </v-card-title>
      <SafeMarkdown :source="recipe.description" />
      <div class="pb-2 d-flex justify-center flex-wrap">
        <RecipeTimeCard
          class="d-flex justify-center flex-wrap"
          :prep-time="recipe.prepTime"
          :total-time="recipe.totalTime"
          :perform-time="recipe.performTime"
        />
        <RecipeRating
          v-if="$vuetify.breakpoint.smAndDown"
          :key="recipe.slug"
          :value="recipe.rating"
          :name="recipe.name"
          :slug="recipe.slug"
        />
      </div>
      <v-divider></v-divider>
    </template>
    <template v-else-if="isEditMode">
      <v-text-field
        v-model="recipe.name"
        class="my-3"
        :label="$t('recipe.recipe-name')"
        :rules="[validators.required]"
      />
      <v-text-field v-model="recipe.recipeYield" dense :label="$t('recipe.servings')" />
      <div class="d-flex flex-wrap" style="gap: 1rem">
        <v-text-field v-model="recipe.totalTime" :label="$t('recipe.total-time')" />
        <v-text-field v-model="recipe.prepTime" :label="$t('recipe.prep-time')" />
        <v-text-field v-model="recipe.performTime" :label="$t('recipe.perform-time')" />
      </div>
      <v-textarea v-model="recipe.description" auto-grow min-height="100" :label="$t('recipe.description')" />
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { validators } from "~/composables/use-validators";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { Recipe } from "~/lib/api/types/recipe";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";

export default defineComponent({
  components: {
    RecipeRating,
    RecipeTimeCard,
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
    const { user } = usePageUser();
    const { imageKey, isEditMode } = usePageState(props.recipe.slug);

    return {
      user,
      imageKey,
      validators,
      isEditMode,
    };
  },
});
</script>
