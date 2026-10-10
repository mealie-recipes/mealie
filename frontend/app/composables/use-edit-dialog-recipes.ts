import { useUserApi } from "~/composables/api";
import type { RecipeSummary } from "~/lib/api/types/recipe";
import type { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";

export const EDIT_DIALOG_RECIPES_PER_PAGE = 10;

/**
 * Pages through the recipes linked to an organizer, alphabetically, for the organizer's edit dialog.
 * Each page is fetched on its own, and a failed page load can be retried without closing the dialog.
 */
export function useEditDialogRecipes(organizerType: "categories" | "foods" | "tools") {
  const api = useUserApi();

  const recipes = ref<RecipeSummary[]>([]);
  const page = ref(1);
  const total = ref(0);
  const loading = ref(false);
  // the page whose load failed, so Retry asks for it again; null when nothing has failed
  const failedPage = ref<number | null>(null);
  const loadFailed = computed(() => failedPage.value !== null);
  const totalPages = computed(() => Math.ceil(total.value / EDIT_DIALOG_RECIPES_PER_PAGE));

  let organizerId: string | null = null;
  // bumped whenever the state is reset, so a response for an earlier dialog visit is dropped
  let requestId = 0;

  function reset() {
    requestId++;
    organizerId = null;
    recipes.value = [];
    page.value = 1;
    total.value = 0;
    loading.value = false;
    failedPage.value = null;
  }

  async function loadPage(target: number) {
    const id = organizerId;
    if (!id || loading.value) {
      return;
    }
    const currentRequestId = requestId;
    let pageGone: boolean | undefined;
    loading.value = true;
    try {
      const query: RecipeSearchQuery = {
        page: target,
        perPage: EDIT_DIALOG_RECIPES_PER_PAGE,
        // names are compared lower-cased; id breaks ties between recipes with the same name so pages stay stable
        orderBy: "name:asc,id:asc",
      };
      query[organizerType] = [id];
      // request failures come back as `error` rather than being thrown
      const { data, error } = await api.recipes.search(query);
      if (currentRequestId !== requestId) {
        return;
      }
      if (error || !data) {
        // the current page stays in view
        failedPage.value = target;
        return;
      }
      failedPage.value = null;
      total.value = data.total ?? 0;
      const items = data.items ?? [];
      // recipes can be unlinked elsewhere while the dialog is open, leaving fewer pages than there were
      pageGone = items.length === 0 && target > 1;
      if (!pageGone) {
        recipes.value = items;
        page.value = target;
      }
    }
    finally {
      if (currentRequestId === requestId) {
        loading.value = false;
      }
    }

    if (pageGone) {
      await loadPage(Math.max(totalPages.value, 1));
    }
  }

  async function open(id: string | null | undefined) {
    reset();
    if (!id) {
      return;
    }
    organizerId = id;
    await loadPage(1);
  }

  async function retry() {
    if (failedPage.value !== null) {
      await loadPage(failedPage.value);
    }
  }

  return { recipes, page, totalPages, loading, loadFailed, open, reset, loadPage, retry };
}
