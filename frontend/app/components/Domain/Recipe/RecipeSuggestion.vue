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
      <div v-for="(organizer, idx) in missingOrganizers" :key="idx">
        <v-col v-if="organizer.show" cols="12">
          <div class="d-flex flex-row flex-wrap align-center pt-2">
            <v-icon class="ma-0 pa-0" />
            <v-card-text class="mr-0 my-0 pl-1 py-0 flex-grow-0" style="width: max-content">
              {{ $t("recipe-finder.missing") }}:
            </v-card-text>
            <v-chip
              v-for="item in organizer.items"
              :key="item.item.id"
              label
              color="secondary custom-transparent"
              class="mr-2 my-1 pl-1"
              variant="flat"
            >
              <v-checkbox dark :ripple="false" hide-details @click="handleCheckbox(item)">
                <template #label>
                  {{ organizer.getLabel(item.item) }}
                </template>
              </v-checkbox>
            </v-chip>
          </div>
        </v-col>
      </div>
      <!-- foods the recipe calls for that the user doesn't have, and what covers them. no
           checkbox: the point is that nothing needs adding to the search -->
      <v-col v-if="substitutedFoods?.length" cols="12">
        <div class="d-flex flex-row flex-wrap align-center pt-2">
          <v-icon class="ma-0 pa-0" />
          <v-card-text class="mr-0 my-0 pl-1 py-0 flex-grow-0" style="width: max-content">
            {{ $t("recipe-finder.substituting") }}:
          </v-card-text>
          <v-chip
            v-for="(substituted, idx) in substitutedFoods"
            :key="idx"
            label
            color="info custom-transparent"
            class="mr-2 my-1"
            variant="flat"
            :prepend-icon="$globals.icons.swapHorizontal"
          >
            {{ $t("recipe-finder.substitute-for-food", {
              substitute: foodLabel(substituted.substituteFood),
              food: foodLabel(substituted.food),
            }) }}
          </v-chip>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import RecipeCardMobile from "./RecipeCardMobile.vue";
import type {
  IngredientFood,
  IngredientFoodSummary,
  RecipeSuggestionSubstitutedFood,
  RecipeSummary,
  RecipeTool,
} from "~/lib/api/types/recipe";

interface Organizer {
  type: "food" | "tool";
  item: IngredientFood | RecipeTool;
  selected: boolean;
}

interface Props {
  recipe: RecipeSummary;
  missingFoods?: IngredientFood[] | null;
  missingTools?: RecipeTool[] | null;
  substitutedFoods?: RecipeSuggestionSubstitutedFood[] | null;
  disableCheckbox?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  missingFoods: null,
  missingTools: null,
  substitutedFoods: null,
  disableCheckbox: false,
});

// same label rule the missing-food chips use
function foodLabel(food: IngredientFood | IngredientFoodSummary) {
  return food.pluralName || food.name;
}

const emit = defineEmits<{
  "add-food": [food: IngredientFood];
  "remove-food": [food: IngredientFood];
  "add-tool": [tool: RecipeTool];
  "remove-tool": [tool: RecipeTool];
}>();

const { $globals } = useNuxtApp();
const missingOrganizers = computed(() => [
  {
    type: "food",
    show: props.missingFoods?.length,
    icon: $globals.icons.foods,
    items: props.missingFoods
      ? props.missingFoods.map((food) => {
          return reactive({ type: "food", item: food, selected: false } as Organizer);
        })
      : [],
    getLabel: (item: IngredientFood) => item.pluralName || item.name,
  },
  {
    type: "tool",
    show: props.missingTools?.length,
    icon: $globals.icons.tools,
    items: props.missingTools
      ? props.missingTools.map((tool) => {
          return reactive({ type: "tool", item: tool, selected: false } as Organizer);
        })
      : [],
    getLabel: (item: RecipeTool) => item.name,
  },
]);

function handleCheckbox(organizer: Organizer) {
  if (props.disableCheckbox) {
    return;
  }

  organizer.selected = !organizer.selected;
  if (organizer.selected) {
    if (organizer.type === "food") {
      emit("add-food", organizer.item as IngredientFood);
    }
    else {
      emit("add-tool", organizer.item as RecipeTool);
    }
  }
  else {
    if (organizer.type === "food") {
      emit("remove-food", organizer.item as IngredientFood);
    }
    else {
      emit("remove-tool", organizer.item as RecipeTool);
    }
  }
}
</script>
