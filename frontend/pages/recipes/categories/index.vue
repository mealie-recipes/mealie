<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="items"
      :items="items"
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
  setup() {
    const { items, actions } = useCategoryStore();

    return {
      items,
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
