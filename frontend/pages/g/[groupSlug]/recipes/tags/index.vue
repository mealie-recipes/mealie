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
      <template #title>
        {{ $t("tag.tags") }}
      </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script lang="ts">
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useTagStore } from "~/composables/store";

export default defineNuxtComponent({
  components: {
    RecipeOrganizerPage,
  },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const { store, actions } = useTagStore();
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("tag.tags"),
    });

    return {
      store,
      actions,
    };
  },
});
</script>
