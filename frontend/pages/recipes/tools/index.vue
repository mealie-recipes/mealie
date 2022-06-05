<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="tools"
      :icon="$globals.icons.potSteam"
      :items="tools"
      item-type="tools"
      @delete="actions.deleteOne"
    >
      <template #title> Tools </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useToolStore } from "~/composables/store";

export default defineComponent({
  components: {
    RecipeOrganizerPage,
  },
  setup() {
    const toolStore = useToolStore();
    const dialog = ref(false);

    return {
      dialog,
      tools: toolStore.items,
      actions: toolStore.actions,
    };
  },
  head: {
    title: "Tools",
  },
});
</script>
