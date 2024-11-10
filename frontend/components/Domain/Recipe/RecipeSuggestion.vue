<template>
  <v-container class="elevation-3">
    <v-row no-gutters>
      <v-col cols="12">
        <RecipeCardMobile
          :name="recipe.name"
          :description="recipe.description"
          :slug="recipe.slug"
          :rating="recipe.rating"
          :image="recipe.image"
          :recipe-id="recipe.id"
        />
      </v-col>
      <v-col v-if="missingFoods && missingFoods.length" cols="12">
        <div class="d-flex flex-row flex-wrap align-center pt-2">
          <v-icon class="ma-0 pa-0">{{ $globals.icons.foods }}</v-icon>
          <v-card-text class="mr-2 my-0 pl-2 py-0" style="width: min-content;">Missing:</v-card-text>
          <v-chip
            v-for="food in missingFoods"
            :key="food.id"
            label
            color="secondary custom-transparent"
            class="mr-2 my-1"
          >
            <span>{{ food.name }}</span>
          </v-chip>
        </div>
      </v-col>
      <v-col v-if="missingTools && missingTools.length" cols="12">
        <div class="d-flex flex-row flex-wrap align-center pt-2">
          <v-icon class="ma-0 pa-0">{{ $globals.icons.tools }}</v-icon>
          <v-card-text class="mr-2 my-0 pl-2 py-0" style="width: min-content;">Missing:</v-card-text>
          <v-chip
            v-for="tool in missingTools"
            :key="tool.id"
            label
            color="secondary custom-transparent"
            class="mr-2 my-1"
          >
            <span>{{ tool.name }}</span>
          </v-chip>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { IngredientFood, RecipeSummary, RecipeTool } from "~/lib/api/types/recipe";
import RecipeCardMobile from "./RecipeCardMobile.vue";

export default defineComponent({
  components: { RecipeCardMobile },
  props: {
    recipe: {
      type: Object as () => RecipeSummary,
      required: true,
    },
    missingFoods: {
      type: Array as () => IngredientFood[] | null,
      default: null,
    },
    missingTools: {
      type: Array as () => RecipeTool[] | null,
      default: null,
    },
  },
  setup() {
    return {};
  }
});
</script>
