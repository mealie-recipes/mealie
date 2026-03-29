<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="store"
      :items="store"
      :icon="$globals.icons.categories"
      item-type="categories"
      @delete="actions.deleteOne"
      @update="actions.updateOne"
    >
      <template #title>
        {{ $t("category.categories") }}
      </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script setup lang="ts">
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useCategoryStore } from "~/composables/store";

definePageMeta({
  middleware: ["group-only"],
});

const { store, actions } = useCategoryStore();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("category.categories"),
});
</script>
