<template>
  <v-list-item
    :active="active"
    :to="recipeRoute"
    :class="{ 'cursor-pointer': !recipeRoute }"
  >
    <template #prepend>
      <v-avatar
        class="recipe-thumbnail"
        rounded="lg"
        width="56"
        height="40"
      >
        <RecipeCardImage
          tiny
          :recipe-id="recipe.id!"
          :slug="recipe.slug"
          :image-version="recipe.image"
          height="40"
          min-height="0"
          :icon-size="24"
        />
      </v-avatar>
    </template>

    <v-list-item-title class="text-truncate">
      {{ recipe.name }}
    </v-list-item-title>
    <v-list-item-subtitle v-if="$slots.subtitle">
      <slot name="subtitle" />
    </v-list-item-subtitle>

    <template
      v-if="$slots.append"
      #append
    >
      <slot name="append" />
    </template>
  </v-list-item>
</template>

<script setup lang="ts">
import RecipeCardImage from "./RecipeCardImage.vue";
import type { RecipeSummary } from "~/lib/api/types/recipe";

interface Props {
  recipe: RecipeSummary;
  active?: boolean;
  disableLink?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  active: false,
  disableLink: false,
});

const auth = useMealieAuth();
const route = useRoute();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const recipeRoute = computed(() => {
  if (props.disableLink || !props.recipe.slug) {
    return undefined;
  }

  return `/g/${groupSlug.value}/r/${props.recipe.slug}`;
});
</script>

<style scoped>
/* the image sizes itself from its own aspect ratio, so stretch it to cover the thumbnail */
.recipe-thumbnail :deep(.v-img) {
  width: 100%;
  height: 100%;
}
</style>
