<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="store"
      :items="store"
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
    const { store, actions } = useTagStore();

    return {
      store,
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
