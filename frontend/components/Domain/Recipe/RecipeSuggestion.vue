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
      <v-col
        v-for="organizer in missingOrganizers"
        v-if="organizer.show"
        cols="12"
      >
        <div class="d-flex flex-row flex-wrap align-center pt-2">
          <v-icon class="ma-0 pa-0">{{ organizer.icon }}</v-icon>
          <v-card-text class="mr-2 my-0 pl-2 py-0" style="width: min-content;">Missing:</v-card-text>
          <v-chip
            v-for="item in organizer.items"
            :key="item.id"
            label
            color="secondary custom-transparent"
            class="mr-2 my-1"
          >
            <span>{{ organizer.getLabel(item) }}</span>
          </v-chip>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
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
  setup(props) {
    const { $globals } = useContext();
    const missingOrganizers = computed(() => [
      // Foods
      {
        show: props.missingFoods?.length,
        icon: $globals.icons.foods,
        items: props.missingFoods,
        getLabel: (item: IngredientFood) => item.pluralName || item.name,
      },
      // Tools
      {
        show: props.missingTools?.length,
        icon: $globals.icons.tools,
        items: props.missingTools,
        getLabel: (item: RecipeTool) => item.name,
      }
    ])

    return {
      missingOrganizers,
    };
  }
});
</script>
