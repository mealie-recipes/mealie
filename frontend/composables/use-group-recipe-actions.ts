import { computed, reactive, ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "./partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { GroupRecipeActionOut, RecipeActionType } from "~/lib/api/types/group";
import { Recipe } from "~/lib/api/types/recipe";

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

export const useGroupRecipeActions = function (
  orderBy: string | null = "title",
  orderDirection: string | null = "asc",
) {
  const api = useUserApi();

  async function refreshGroupRecipeActions() {
    loading.value = true;
    const { data } = await api.groupRecipeActions.getAll(1, -1, { orderBy, orderDirection });
    groupRecipeActions.value = data?.items || null;
    loading.value = false;
  }

  const recipeActions = computed<GroupRecipeActionOut[] | null>(() => {
    return groupRecipeActions.value;
  });

  function parseRecipeActionUrl(url: string, recipe: Recipe): string {
    /* eslint-disable no-template-curly-in-string */
    return url
      .replace("${url}", window.location.href)
      .replace("${id}", recipe.id || "")
      .replace("${slug}", recipe.slug || "")
    /* eslint-enable no-template-curly-in-string */
  };

  async function execute(action: GroupRecipeActionOut, recipe: Recipe) {
    const url = parseRecipeActionUrl(action.url, recipe);

    switch (action.actionType) {
      case "link":
        window.open(url, "_blank")?.focus();
        break;
      case "post":
        await fetch(url, {
          method: "POST",
          headers: {
            // The "text/plain" content type header is used here to skip the CORS preflight request,
            // since it may fail. This is fine, since we don't care about the response, we just want
            // the request to get sent.
            "Content-Type": "text/plain",
          },
          body: JSON.stringify(recipe),
        }).catch((error) => {
          console.error(error);
        });
        break;
      default:
        break;
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
    execute,
    recipeActions,
  };
};
