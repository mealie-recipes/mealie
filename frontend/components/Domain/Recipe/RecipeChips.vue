<template>
  <div v-if="items.length > 0">
    <h2
      v-if="title"
      class="mt-4"
    >
      {{ title }}
    </h2>
    <v-chip
      v-for="item in items.slice(0, limit)"
      :key="item.name"
      label
      class="mr-1 mt-1"
      :color="getChipColor(item)"
      variant="flat"
      :size="small ? 'small' : 'default'"
      dark

      @click.prevent="() => $emit('item-selected', item, urlPrefix)"
    >
      {{ truncateText(item.name) }}
    </v-chip>
  </div>
</template>

<script setup lang="ts">
import type { RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { useTagGroupStore } from "~/composables/store";

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

const { store: tagGroups } = useTagGroupStore();

function getChipColor(item: RecipeCategory | RecipeTag | RecipeTool): string {
  if ("tagGroupId" in item && item.tagGroupId) {
    const group = tagGroups.value.find(g => g.id === item.tagGroupId);
    if (group?.color) return group.color;
  }
  return "accent";
}

function truncateText(text: string, length = 20, clamp = "...") {
  if (!props.truncate) return text;
  const node = document.createElement("div");
  node.innerHTML = text;
  const content = node.textContent || "";
  return content.length > length ? content.slice(0, length) + clamp : content;
}
</script>

<style></style>
