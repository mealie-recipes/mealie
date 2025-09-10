<template>
  <v-container>
    <RecipeOrganizerPage
      v-if="tools"
      :icon="$globals.icons.potSteam"
      :items="tools"
      item-type="tools"
      @delete="deleteOne"
      @update="updateOne"
    >
      <template #title>
        {{ $t("tool.tools") }}
      </template>
    </RecipeOrganizerPage>
  </v-container>
</template>

<script lang="ts">
import RecipeOrganizerPage from "~/components/Domain/Recipe/RecipeOrganizerPage.vue";
import { useToolStore } from "~/composables/store";
import type { RecipeTool } from "~/lib/api/types/recipe";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

export default defineNuxtComponent({
  components: {
    RecipeOrganizerPage,
  },
  middleware: ["sidebase-auth", "group-only"],
  setup() {
    const $auth = useMealieAuth();
    const toolStore = useToolStore();
    const dialog = ref(false);
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("tool.tools"),
    });

    const userHousehold = computed(() => $auth.user.value?.householdSlug || "");
    const tools = computed(() => toolStore.store.value.map(tool => (
      {
        ...tool,
        onHand: tool.householdsWithTool?.includes(userHousehold.value) || false,
      } as RecipeToolWithOnHand
    )));

    async function deleteOne(id: string | number) {
      await toolStore.actions.deleteOne(id);
    }

    async function updateOne(tool: RecipeToolWithOnHand) {
      if (userHousehold.value) {
        if (tool.onHand && !tool.householdsWithTool?.includes(userHousehold.value)) {
          if (!tool.householdsWithTool) {
            tool.householdsWithTool = [userHousehold.value];
          }
          else {
            tool.householdsWithTool.push(userHousehold.value);
          }
        }
        else if (!tool.onHand && tool.householdsWithTool?.includes(userHousehold.value)) {
          tool.householdsWithTool = tool.householdsWithTool.filter(household => household !== userHousehold.value);
        }
      }
      await toolStore.actions.updateOne(tool);
    }

    return {
      dialog,
      tools,
      deleteOne,
      updateOne,
    };
  },
});
</script>
