<template>
  <div v-if="recipes.length > 0 || loadFailed" class="mt-4">
    <div class="text-subtitle-2 mb-1">
      {{ $t("data-pages.associated-recipes") }}
    </div>
    <v-list density="compact">
      <v-list-item
        v-for="recipe in recipes"
        :key="recipe.slug"
        :to="`/g/${groupSlug}/r/${recipe.slug}`"
        :title="recipe.name || recipe.slug"
      />
    </v-list>
    <div v-if="loadFailed" class="d-flex align-center text-body-2 pl-2">
      <span class="text-error">{{ $t("data-pages.load-recipes-failed") }}</span>
      <v-btn
        variant="text"
        size="small"
        color="primary"
        class="ml-2"
        :loading="loading"
        @click="emit('retry')"
      >
        {{ $t("data-pages.retry") }}
      </v-btn>
    </div>
    <div v-if="totalPages > 1" class="d-flex align-center mt-2">
      <v-btn
        variant="text"
        size="small"
        :disabled="page <= 1 || loading"
        @click="emit('load-page', page - 1)"
      >
        {{ $t("general.previous") }}
      </v-btn>
      <span class="text-body-2 mx-2">{{ page }} / {{ totalPages }}</span>
      <v-btn
        variant="text"
        size="small"
        :disabled="page >= totalPages || loading"
        @click="emit('load-page', page + 1)"
      >
        {{ $t("general.next") }}
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RecipeSummary } from "~/lib/api/types/recipe";

/**
 * Read-only list of the recipes linked to an organizer, shown at the bottom of its edit dialog.
 * State comes from useEditDialogRecipes in the page, which also owns opening and resetting it.
 */
defineProps<{
  recipes: RecipeSummary[];
  page: number;
  totalPages: number;
  loading: boolean;
  loadFailed: boolean;
  groupSlug: string;
}>();

const emit = defineEmits<{
  (e: "load-page", page: number): void;
  (e: "retry"): void;
}>();
</script>
