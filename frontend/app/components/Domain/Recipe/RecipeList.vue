<template>
  <v-list :class="attrs.class.list">
    <v-sheet
      v-for="recipe, index in recipes"
      :key="recipe.id || recipe.slug"
      :elevation="2"
      :class="attrs.class.sheet"
      :style="attrs.style.sheet"
    >
      <v-list-item
        :to="disabled ? '' : '/g/' + groupSlug + '/r/' + recipe.slug"
        :class="attrs.class.listItem"
      >
        <template #prepend>
          <v-avatar color="primary" :class="attrs.class.avatar">
            <v-img
              v-if="recipe.image"
              :src="getRecipeImageUrl(recipe)"
            />
            <v-icon
              v-else
              :class="attrs.class.icon"
              dark
              size="x-large"
            >
              {{ $globals.icons.primary }}
            </v-icon>
          </v-avatar>
        </template>
        <div :class="attrs.class.text">
          <v-list-item-title
            :class="listItem && listItemDescriptions[index] ? '' : 'pr-4'"
            :style="attrs.style.text.title"
          >
            {{ recipe.name }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="showDescription">
            {{ recipe.description }}
          </v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="listItem && listItemDescriptions[index]"
            :style="attrs.style.text.subTitle"
          >
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div v-html="listItemDescriptions[index]" />
          </v-list-item-subtitle>
        </div>
        <template #append>
          <slot
            :name="'actions-' + recipe.id"
            :v-bind="{ item: recipe }"
          />
        </template>
      </v-list-item>
    </v-sheet>
  </v-list>
</template>

<script setup lang="ts">
import DOMPurify from "dompurify";
import { useFraction } from "~/composables/recipes/use-fraction";
import { useStaticRoutes } from "~/composables/api";
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

const auth = useMealieAuth();
const { frac } = useFraction();
const { recipeTinyImage } = useStaticRoutes();
const route = useRoute();
const display = useDisplay();
const groupSlug = computed(() => route.params.groupSlug || auth.user?.value?.groupSlug || "");

// Determine if we should show tiles based on screen size and number of recipes
const shouldShowTiles = computed(() => {
  return props.tile && display.smAndUp.value;
});

function getRecipeImageUrl(recipe: RecipeSummary) {
  return recipeTinyImage(String(recipe.id), recipe.image ?? "");
}

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
      avatar: "",
      icon: "pa-1 primary",
      text: "",
    },
    style: {
      sheet: sheetStyle,
      text: {
        title: "",
        subTitle: "",
      },
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
