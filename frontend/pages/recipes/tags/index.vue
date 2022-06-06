<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="items"
      :items="items"
      :icon="$globals.icons.tags"
      item-type="tags"
      @delete="actions.deleteOne"
    >
      <template #title> Tags </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useTagStore } from "~/composables/store";

export default defineComponent({
  components: {
    RecipeOrganizerPage,
  },
  setup() {
    const { items, actions } = useTagStore();

    return {
      items,
      actions,
    };
  },
  head: {
    title: "Tags",
  },
});
</script>
