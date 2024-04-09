import { computed, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { GroupRecipeActionOut } from "~/lib/api/types/group";

const groupRecipeActions = ref<GroupRecipeActionOut[] | null>(null);
const loading = ref(false);

export const useGroupRecipeActions = function () {
  const api = useUserApi();
  async function refreshGroupRecipeActions() {
    loading.value = true;
    const { data } = await api.groupRecipeActions.getAll(1, -1);
    groupRecipeActions.value = data?.items || null;
    loading.value = false;
  }

  const recipeActions = computed<GroupRecipeActionOut[] | null>(() => {
    if (groupRecipeActions.value === null) {
      return null;
    }

    return groupRecipeActions.value.map(action => {
      action.url = parseRecipeActionUrl(action.url);
      return action;
    });
  });

  function parseRecipeActionUrl(url: string): string {
    return url.replace("${url}", window.location.href)
  };

  async function executeRecipeAction(action: GroupRecipeActionOut) {
    switch (action.actionType) {
      case "link":
        window.open(action.url, "_blank")?.focus();
        return;
      default:
        return;
    }
  };

  if (!groupRecipeActions.value && !loading.value) {
    refreshGroupRecipeActions();
  };

  return {
    executeRecipeAction,
    recipeActions,
  };
};
