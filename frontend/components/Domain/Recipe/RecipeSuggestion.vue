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
        <v-col
          v-if="organizer.show"
          cols="12"
        >
          <div class="d-flex flex-row flex-wrap align-center pt-2">
            <v-icon class="ma-0 pa-0">{{ organizer.icon }}</v-icon>
            <v-card-text class="mr-0 my-0 pl-1 py-0" style="width: min-content;">
              {{ $tc("recipe-finder.missing") }}:
            </v-card-text>
            <v-chip
              v-for="item in organizer.items"
              :key="item.item.id"
              label
              color="secondary custom-transparent"
              class="mr-2 my-1"
            >
              <v-checkbox dark :ripple="false" @click="handleCheckbox(item)">
                <template #label>
                  {{ organizer.getLabel(item.item) }}
                </template>
              </v-checkbox>
            </v-chip>
          </div>
        </v-col>
      </div>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, useContext } from "@nuxtjs/composition-api";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { IngredientFood, RecipeSummary, RecipeTool } from "~/lib/api/types/recipe";

interface Organizer {
  type: "food" | "tool";
  item: IngredientFood | RecipeTool;
  selected: boolean;
}

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
    disableCheckbox: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const { $globals } = useContext();
    const missingOrganizers = computed(() => [
      {
        type: "food",
        show: props.missingFoods?.length,
        icon: $globals.icons.foods,
        items: props.missingFoods ? props.missingFoods.map((food) => {
          return reactive({type: "food", item: food, selected: false} as Organizer);
        }) : [],
        getLabel: (item: IngredientFood) => item.pluralName || item.name,
      },
      {
        type: "tool",
        show: props.missingTools?.length,
        icon: $globals.icons.tools,
        items: props.missingTools ? props.missingTools.map((tool) => {
          return reactive({type: "tool", item: tool, selected: false} as Organizer);
        }) : [],
        getLabel: (item: RecipeTool) => item.name,
      }
    ])

    function handleCheckbox(organizer: Organizer) {
      if (props.disableCheckbox) {
        return;
      }

      organizer.selected = !organizer.selected;
      if (organizer.selected) {
        context.emit(`add-${organizer.type}`, organizer.item);
      }
      else {
        context.emit(`remove-${organizer.type}`, organizer.item);
      }
    }

    return {
      missingOrganizers,
      handleCheckbox,
    };
  }
});
</script>
