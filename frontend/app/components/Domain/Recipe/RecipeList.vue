<template>
  <v-list :class="attrs.class.list">
    <v-sheet
      v-for="recipe, index in recipes"
      :key="recipe.id || recipe.slug"
      :elevation="2"
      :class="attrs.class.sheet"
      :style="attrs.style.sheet"
    >
      <RecipeCardLineItem
        :recipe="recipe"
        :disable-link="disabled"
        :class="attrs.class.listItem"
      >
        <template
          v-if="showDescription || (listItem && listItemDescriptions[index])"
          #subtitle
        >
          <div v-if="showDescription">
            {{ recipe.description }}
          </div>
          <template v-if="listItem && listItemDescriptions[index]">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div v-html="listItemDescriptions[index]" />
          </template>
        </template>
        <template #append>
          <slot
            :name="'actions-' + recipe.id"
            :v-bind="{ item: recipe }"
          />
        </template>
      </RecipeCardLineItem>
    </v-sheet>
  </v-list>
</template>

<script setup lang="ts">
import DOMPurify from "dompurify";
import RecipeCardLineItem from "./RecipeCardLineItem.vue";
import { useFraction } from "~/composables/recipes/use-fraction";
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import type { RecipeSummary } from "~/lib/api/types/recipe";

interface Props {
  recipes: RecipeSummary[];
  listItem?: ShoppingListItemOut;
  tile?: boolean;
  showDescription?: boolean;
  disabled?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  listItem: undefined,
  tile: false,
  showDescription: false,
  disabled: false,
});

const { frac } = useFraction();
const display = useDisplay();

// Determine if we should show tiles based on screen size and number of recipes
const shouldShowTiles = computed(() => {
  return props.tile && display.smAndUp.value;
});

const attrs = computed(() => {
  const tileClasses = shouldShowTiles.value ? "d-flex flex-wrap" : "bg-transparent";
  const sheetClasses = shouldShowTiles.value
    ? "flex-grow-0 flex-shrink-0 mb-2 me-3"
    : props.tile ? "mb-2 mx-2" : "mb-1";
  const sheetStyle = shouldShowTiles.value
    ? { flexBasis: "calc(50% - 12px)", width: "calc(50% - 12px)" }
    : {};

  return {
    class: {
      list: tileClasses,
      sheet: sheetClasses,
      listItem: "px-4 py-2",
    },
    style: {
      sheet: sheetStyle,
    },
  };
});

function sanitizeHTML(rawHtml: string) {
  return DOMPurify.sanitize(rawHtml, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: ["strong", "sup"],
  });
}

const listItemDescriptions = computed<string[]>(() => {
  if (
    props.recipes.length === 1 // we don't need to specify details if there's only one recipe ref
    || !props.listItem?.recipeReferences
    || props.listItem.recipeReferences.length !== props.recipes.length
  ) {
    return props.recipes.map(_ => "");
  }

  const listItemDescriptions: string[] = [];
  for (let i = 0; i < props.recipes.length; i++) {
    const itemRef = props.listItem?.recipeReferences[i];
    const quantity = (itemRef.recipeQuantity || 1) * (itemRef.recipeScale || 1);

    let listItemDescription = "";
    if (props.listItem.unit?.fraction) {
      const fraction = frac(quantity, 10, true);
      if (fraction[0] !== undefined && fraction[0] > 0) {
        listItemDescription += fraction[0];
      }

      if (fraction[1] > 0) {
        listItemDescription += ` <sup>${fraction[1]}</sup>&frasl;<sub>${fraction[2]}</sub>`;
      }
      else {
        listItemDescription = (quantity).toString();
      }
    }
    else {
      listItemDescription = (Math.round(quantity * 100) / 100).toString();
    }

    if (props.listItem.unit) {
      const unitDisplay = props.listItem.unit.useAbbreviation && props.listItem.unit.abbreviation
        ? props.listItem.unit.abbreviation
        : props.listItem.unit.name;

      listItemDescription += ` ${unitDisplay}`;
    }
    if (props.listItem.food) {
      const foodName = props.listItem.food.name;
      listItemDescription += ` ${foodName}`;
    }

    if (itemRef.recipeNote) {
      listItemDescription += `, ${itemRef.recipeNote}`;
    }

    listItemDescriptions.push(sanitizeHTML(listItemDescription));
  }

  return listItemDescriptions;
});
</script>
