import { useOnline, useIdle } from "@vueuse/core";
import type { ShoppingListOut } from "~/lib/api/types/household";
import { useShoppingListItemActions } from "~/composables/use-shopping-list-item-actions";

/**
 * Composable for managing shopping list data fetching and polling
 */
export function useShoppingListData(listId: string, shoppingList: Ref<ShoppingListOut | null>, loadingCounter: Ref<number>) {
  const isOffline = computed(() => useOnline().value === false);
  const { idle } = useIdle(5 * 60 * 1000); // 5 minutes
  const shoppingListItemActions = useShoppingListItemActions(listId);

  async function fetchShoppingList() {
    const data = await shoppingListItemActions.getList();
    return data;
  }

  async function refresh(updateListItemOrder: () => void) {
    loadingCounter.value += 1;
    try {
      await shoppingListItemActions.process();
    }
    catch (error) {
      console.error(error);
    }

    let newListValue: typeof shoppingList.value = null;
    try {
      newListValue = await fetchShoppingList();
    }
    catch (error) {
      console.error(error);
    }

    loadingCounter.value -= 1;

    // only update the list with the new value if we're not loading, to prevent UI jitter
    if (loadingCounter.value) {
      return;
    }

    // Prevent overwriting local changes with stale backend data when offline
    if (isOffline.value) {
      // Do not update shoppingList.value from backend when offline
      updateListItemOrder();
      return;
    }

    // if we're not connected to the network, this will be null, so we don't want to clear the list
    if (newListValue) {
      shoppingList.value = newListValue;
    }

    updateListItemOrder();
  }

  // constantly polls for changes
  async function pollForChanges(updateListItemOrder: () => void) {
    // pause polling if the user isn't active or we're busy
    if (idle.value || loadingCounter.value) {
      return;
    }

    try {
      await refresh(updateListItemOrder);

      if (shoppingList.value) {
        attempts = 0;
        return;
      }

      // if the refresh was unsuccessful, the shopping list will be null, so we increment the attempt counter
      attempts++;
    }
    catch {
      attempts++;
    }

    // if we hit too many errors, stop polling
    if (attempts >= maxAttempts) {
      clearInterval(pollTimer);
    }
  }

  // start polling
  loadingCounter.value -= 1;

  // max poll time = pollFrequency * maxAttempts = 24 hours
  // we use a long max poll time since polling stops when the user is idle anyway
  const pollFrequency = 5000;
  const maxAttempts = 17280;
  let attempts = 0;
  let pollTimer: ReturnType<typeof setInterval>;

  function startPolling(updateListItemOrder: () => void) {
    pollForChanges(updateListItemOrder); // populate initial list

    pollTimer = setInterval(() => {
      pollForChanges(updateListItemOrder);
    }, pollFrequency);
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
    }
  }

  return {
    isOffline,
    fetchShoppingList,
    refresh,
    startPolling,
    stopPolling,
    shoppingListItemActions,
  };
}
