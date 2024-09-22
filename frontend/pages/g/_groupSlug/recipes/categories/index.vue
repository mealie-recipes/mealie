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
      <template #title> {{ $tc("category.categories") }} </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useCategoryStore } from "~/composables/store";

export default defineComponent({
  components: {
    RecipeOrganizerPage,
  },
  middleware: ["auth", "group-only"],
  setup() {
    const { store, actions } = useCategoryStore();

    return {
      store,
      actions,
    };
  },
  head() {
    return {
      title: this.$tc("category.categories"),
    };
  },
});
</script>
