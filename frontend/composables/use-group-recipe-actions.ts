import { computed, reactive, ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "./partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { GroupRecipeActionOut, RecipeActionType } from "~/lib/api/types/group";

const groupRecipeActions = ref<GroupRecipeActionOut[] | null>(null);
const loading = ref(false);

export function useGroupRecipeActionData() {
  const data = reactive({
    id: "",
    actionType: "link" as RecipeActionType,
    title: "",
    url: "",
  });

  function reset() {
    data.id = "";
    data.actionType = "link";
    data.title = "";
    data.url = "";
  }

  return {
    data,
    reset,
  };
}

export const useGroupRecipeActions = function (orderBy: string = "title", orderDirection: string = "asc") {
  const api = useUserApi();
  async function refreshGroupRecipeActions() {
    loading.value = true;
    const { data } = await api.groupRecipeActions.getAll(1, -1, { orderBy, orderDirection });
    groupRecipeActions.value = data?.items || null;
    loading.value = false;
  }

  const recipeActionsData = computed<GroupRecipeActionOut[] | null>(() => {
    return groupRecipeActions.value;
  });

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

  const actions = {
    ...useStoreActions<GroupRecipeActionOut>(api.groupRecipeActions, groupRecipeActions, loading),
    flushStore() {
      groupRecipeActions.value = [];
    }
  }

  return {
    actions,
    executeRecipeAction,
    recipeActions,
    recipeActionsData,
  };
};
