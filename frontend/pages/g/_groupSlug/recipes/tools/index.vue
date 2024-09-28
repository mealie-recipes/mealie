<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="tools"
      :icon="$globals.icons.potSteam"
      :items="tools"
      item-type="tools"
      @delete="actions.deleteOne"
      @update="actions.updateOne"
    >
      <template #title> {{ $t("tool.tools") }} </template>
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
  middleware: ["auth", "group-only"],
  setup() {
    const toolStore = useToolStore();
    const dialog = ref(false);

    return {
      dialog,
      tools: toolStore.store,
      actions: toolStore.actions,
    };
  },
  head() {
    return {
      title: this.$tc("tool.tools"),
    };
  },
});
</script>
