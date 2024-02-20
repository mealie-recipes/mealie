<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="items"
      :items="items"
      :icon="$globals.icons.tags"
      item-type="tags"
      @delete="actions.deleteOne"
      @update="actions.updateOne"
    >
      <template #title> {{ $t("tag.tags") }} </template>
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
  middleware: ["auth", "group-only"],
  setup() {
    const { items, actions } = useTagStore();

    return {
      items,
      actions,
    };
  },
  head() {
    return {
      title: this.$tc("tag.tags"),
    };
  },
});
</script>
