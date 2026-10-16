<template>
  <div v-if="items.length > 0">
    <h2
      v-if="title"
      class="mt-4"
    >
      {{ title }}
    </h2>
    <v-chip
      v-for="category in items.slice(0, limit)"
      :key="category.name"
      label
      class="mr-1 mt-1"
      :color="chipColor(category)"
      variant="flat"
      :size="small ? 'small' : 'default'"
      dark

      @click.prevent="() => $emit('item-selected', category, urlPrefix)"
    >
      {{ truncateText(category.name) }}
    </v-chip>
  </div>
</template>

<script setup lang="ts">
import type { RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { truncateText as truncatePlainText } from "~/lib/sanitize/text";

export type UrlPrefixParam = "tags" | "categories" | "tools";

interface Props {
  truncate?: boolean;
  items?: RecipeCategory[] | RecipeTag[] | RecipeTool[];
  title?: boolean;
  urlPrefix?: UrlPrefixParam;
  limit?: number;
  small?: boolean;
  maxWidth?: string | null;
}
const props = withDefaults(defineProps<Props>(), {
  truncate: false,
  items: () => [],
  title: false,
  urlPrefix: "categories",
  limit: 999,
  small: false,
  maxWidth: null,
});

defineEmits(["item-selected"]);

interface ColorableItem {
  color?: string | null;
}

/**
 * Tags and categories carry an optional display color; when unset the chip
 * keeps the historical theme accent default. (The generated API types gain the
 * optional `color` field after `task dev:generate`; the cast keeps this
 * component type-safe either way.)
 */
function chipColor(item: RecipeCategory | RecipeTag | RecipeTool): string {
  return (item as ColorableItem).color || "accent";
}

function truncateText(text: string, length = 20, clamp = "...") {
  if (!props.truncate) return text;
  return truncatePlainText(text, length, clamp);
}
</script>

<style></style>
