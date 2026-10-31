import { useStoreActions } from "./partials/use-actions-factory";
import { alert } from "./use-toast";
import { useUserApi } from "~/composables/api";
import type { GroupRecipeActionOut, GroupRecipeActionType } from "~/lib/api/types/household";
import type { RequestResponse } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const groupRecipeActions = ref<GroupRecipeActionOut[] | null>(null);
const loading = ref(false);

const shareLinkFieldPattern = /\$\{share-link-expires-seconds-(\d+)\}/g;

export function getShareLinkFields(url: string): { field: string; seconds: number }[] {
  const fields = new Map<string, number>();
  for (const match of url.matchAll(shareLinkFieldPattern)) {
    const seconds = parseInt(match[1] as string);
    if (seconds > 0) {
      fields.set(match[0], seconds);
    }
  }

  return Array.from(fields, ([field, seconds]) => ({ field, seconds }));
}

export function resetGroupRecipeActions() {
  groupRecipeActions.value = null;
  loading.value = false;
}

export function useGroupRecipeActionData() {
  const data = reactive({
    id: "",
    actionType: "link" as GroupRecipeActionType,
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
  const auth = useMealieAuth();
  const route = useRoute();
  const i18n = useI18n();

  async function refreshGroupRecipeActions() {
    loading.value = true;
    const { data } = await api.groupRecipeActions.getAll(1, -1, { orderBy, orderDirection });
    groupRecipeActions.value = data?.items || null;
    loading.value = false;
  }

  const recipeActions = computed<GroupRecipeActionOut[] | null>(() => {
    return groupRecipeActions.value;
  });

  async function createShareLink(recipe: Recipe, seconds: number): Promise<string | null> {
    const { data } = await api.recipes.share.createOne({
      recipeId: recipe.id || "",
      expiresAt: new Date(Date.now() + seconds * 1000).toISOString(),
    });
    if (!data?.id) {
      return null;
    }

    const groupSlug = route.params.groupSlug as string || auth.user.value?.groupSlug || "";
    return `${window.location.origin}/g/${groupSlug}/shared/r/${data.id}`;
  }

  async function insertShareLinks(url: string, recipe: Recipe): Promise<string | null> {
    for (const { field, seconds } of getShareLinkFields(url)) {
      const shareLink = await createShareLink(recipe, seconds);
      if (!shareLink) {
        return null;
      }
      url = url.replaceAll(field, shareLink);
    }

    return url;
  }

  function parseRecipeActionUrl(url: string, recipe: Recipe, recipeScale: number): string {
    const recipeServings = (recipe.recipeServings || 1) * recipeScale;
    const recipeYieldQuantity = (recipe.recipeYieldQuantity || 1) * recipeScale;

    return url
      .replace("${url}", window.location.href)
      .replace("${id}", recipe.id || "")
      .replace("${slug}", recipe.slug || "")
      .replace("${servings}", recipeServings.toString())
      .replace("${yieldQuantity}", recipeYieldQuantity.toString())
      .replace("${yieldText}", recipe.recipeYield || "");
  };

  // eslint-disable-next-line @typescript-eslint/no-invalid-void-type
  async function execute(action: GroupRecipeActionOut, recipe: Recipe, recipeScale: number): Promise<void | RequestResponse<unknown>> {
    switch (action.actionType) {
      case "link": {
        if (!getShareLinkFields(action.url).length) {
          window.open(parseRecipeActionUrl(action.url, recipe, recipeScale), "_blank")?.focus();
          return;
        }

        // browsers may block window.open after an await, so open the tab before creating the share links
        const tab = window.open("", "_blank");
        const url = await insertShareLinks(action.url, recipe).catch(() => null);
        if (!url) {
          tab?.close();
          alert.error(i18n.t("events.something-went-wrong"));
          return;
        }

        const parsedUrl = parseRecipeActionUrl(url, recipe, recipeScale);
        if (tab) {
          tab.location.href = parsedUrl;
          tab.focus();
        }
        else {
          window.open(parsedUrl, "_blank")?.focus();
        }
        return;
      }
      case "post":
        return await api.groupRecipeActions.triggerAction(action.id, recipe.slug || "", recipeScale);
      default:
        break;
    }
  };

  if (!groupRecipeActions.value && !loading.value) {
    refreshGroupRecipeActions();
  };

  const actions = {
    ...useStoreActions<GroupRecipeActionOut>(
      "group-recipe-actions",
      api.groupRecipeActions,
      groupRecipeActions,
      loading,
      { orderBy: orderBy },
    ),
  };

  return {
    actions,
    execute,
    recipeActions,
  };
};
