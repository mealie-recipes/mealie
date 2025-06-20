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

<script lang="ts">
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useCategoryStore } from "~/composables/store";

export default defineNuxtComponent({
  components: {
    RecipeOrganizerPage,
  },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const { store, actions } = useCategoryStore();
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("category.categories"),
    });

    return {
      store,
      actions,
    };
  },
});
</script>
