import { useLocalStorage, useOnline } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import type { ShoppingListItemOut, ShoppingListOut } from "~/lib/api/types/household";
import type { RequestResponse } from "~/lib/api/types/non-generated";

const localStorageKey = "shopping-list-queue";
const queueTimeout = 5 * 60 * 1000; // 5 minutes

type ItemQueueType = "create" | "update" | "delete";

export interface ShoppingListQueue {
  create: ShoppingListItemOut[];
  update: ShoppingListItemOut[];
  delete: ShoppingListItemOut[];

  lastUpdate: number;
}

interface Storage {
  [key: string]: ShoppingListQueue;
}

export function useShoppingListItemActions(shoppingListId: string) {
  const isOnline = useOnline();
  const api = useUserApi();
  const storage = useLocalStorage(localStorageKey, {} as Storage, { deep: true });
  const queue = reactive(getQueue());
  const queueEmpty = computed(() => !queue.create.length && !queue.update.length && !queue.delete.length);
  if (queueEmpty.value) {
    queue.lastUpdate = Date.now();
  }

  storage.value[shoppingListId] = { ...queue };
  watch(
    () => queue,
    (value) => {
      storage.value[shoppingListId] = { ...value };
    },
    {
      deep: true,
      immediate: true,
    },
  );

  function isValidQueueObject(obj: any): obj is ShoppingListQueue {
    if (typeof obj !== "object" || obj === null) {
      return false;
    }

    const hasRequiredProps = "create" in obj && "update" in obj && "delete" in obj && "lastUpdate" in obj;
    if (!hasRequiredProps) {
      return false;
    }

    const arraysValid = Array.isArray(obj.create) && Array.isArray(obj.update) && Array.isArray(obj.delete);

    const lastUpdateValid = typeof obj.lastUpdate === "number" && !isNaN(new Date(obj.lastUpdate).getTime());

    return arraysValid && lastUpdateValid;
  }

  function createEmptyQueue(): ShoppingListQueue {
    const newQueue = { create: [], update: [], delete: [], lastUpdate: Date.now() };
    return newQueue;
  }

  function getQueue(): ShoppingListQueue {
    try {
      const fetchedQueue = storage.value[shoppingListId];
      if (!isValidQueueObject(fetchedQueue)) {
        console.log("Invalid queue object in local storage; resetting queue.");
        return createEmptyQueue();
      }
      else {
        return fetchedQueue;
      }
    }
    catch (error) {
      console.log("Error validating queue object in local storage; resetting queue.", error);
      return createEmptyQueue();
    }
  }

  function removeFromQueue(itemQueue: ShoppingListItemOut[], item: ShoppingListItemOut): boolean {
    const index = itemQueue.findIndex(i => i.id === item.id);
    if (index === -1) {
      return false;
    }

    itemQueue.splice(index, 1);
    return true;
  }

  function mergeListItemsByLatest(
    list1: ShoppingListItemOut[],
    list2: ShoppingListItemOut[],
  ) {
    const mergedList = [...list1];
    list2.forEach((list2Item) => {
      const conflictingItem = mergedList.find(item => item.id === list2Item.id);
      if (conflictingItem
        && list2Item.updatedAt && conflictingItem.updatedAt
        && list2Item.updatedAt > conflictingItem.updatedAt) {
        mergedList.splice(mergedList.indexOf(conflictingItem), 1, list2Item);
      }
      else if (!conflictingItem) {
        mergedList.push(list2Item);
      }
    });
    return mergedList;
  }

  async function getList() {
    const response = await api.shopping.lists.getOne(shoppingListId);
    if (response.data) {
      // Merge pending local changes (both online and offline)
      const createAndUpdateQueues = mergeListItemsByLatest(queue.update, queue.create);
      const deleteQueueIds = new Set(queue.delete.map(item => item.id));

      const filteredLocalChanges = createAndUpdateQueues.filter(item => !deleteQueueIds.has(item.id));
      let mergedItems = mergeListItemsByLatest(response.data.listItems ?? [], filteredLocalChanges);
      mergedItems = mergedItems.filter(item => !deleteQueueIds.has(item.id));

      response.data.listItems = mergedItems;
    }
    return response.data;
  }

  function createItem(item: ShoppingListItemOut) {
    removeFromQueue(queue.create, item);
    removeFromQueue(queue.update, item);
    removeFromQueue(queue.delete, item);

    queue.create.push(item);
  }

  function updateItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromQueue(queue.create, item);
    removeFromQueue(queue.update, item);
    removeFromQueue(queue.delete, item);

    if (removedFromCreate) {
      // This item hasn't been created yet, so keep it in create queue with updated data
      queue.create.push(item);
    }
    else {
      queue.update.push(item);
    }
  }

  function deleteItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromQueue(queue.create, item);
    if (removedFromCreate) {
      // This item hasn't been created yet, so we don't need to delete it
      return;
    }

    removeFromQueue(queue.update, item);
    removeFromQueue(queue.delete, item);
    queue.delete.push(item);
  }

  function getQueueItems(itemQueueType: ItemQueueType) {
    return queue[itemQueueType];
  }

  function clearQueueItems(itemQueueType: ItemQueueType | "all", itemIds: string[] | null = null) {
    if (itemQueueType === "create" || itemQueueType === "all") {
      queue.create = itemIds ? queue.create.filter(item => !itemIds.includes(item.id)) : [];
    }
    if (itemQueueType === "update" || itemQueueType === "all") {
      queue.update = itemIds ? queue.update.filter(item => !itemIds.includes(item.id)) : [];
    }
    if (itemQueueType === "delete" || itemQueueType === "all") {
      queue.delete = itemIds ? queue.delete.filter(item => !itemIds.includes(item.id)) : [];
    }
    if (queueEmpty.value) {
      queue.lastUpdate = Date.now();
    }
  }

  function checkUpdateState(list: ShoppingListOut) {
    const cutoffDate = new Date(queue.lastUpdate + queueTimeout).toISOString();
    if (list.updatedAt && list.updatedAt > cutoffDate) {
      // If the queue is too far behind the shopping list to reliably do updates, we clear the queue
      console.log("Out of sync with server; clearing queue");
      clearQueueItems("all");
    }
  }

  // Whether a write failed during the current process run, leaving its items queued
  let failedWriteInRun = false;

  // Whether the last completed run couldn't save everything, so the page can tell the user
  const hasFailedWrites = ref(false);

  /**
   * Whether the server answered that it won't take this request, as opposed to a failure that may pass by itself.
   */
  function isRejection(error: any): boolean {
    const status: number | undefined = error?.response?.status;
    return !!status && status >= 400 && status < 500 && ![401, 408, 429].includes(status);
  }

  /**
   * Processes the queue items and returns false if there was an unexpected error, which resets the queue.
   * A failed write isn't unexpected; its items stay queued and are sent again on the next run.
   */
  async function processQueueItems(
    action: (items: ShoppingListItemOut[]) => Promise<RequestResponse<any>>,
    itemQueueType: ItemQueueType,
  ): Promise<boolean> {
    let queueItems: ShoppingListItemOut[];
    try {
      queueItems = getQueueItems(itemQueueType);
      if (!queueItems.length) {
        return true;
      }
    }
    catch (error) {
      console.log(`Error fetching queue items of type ${itemQueueType}:`, error);
      clearQueueItems(itemQueueType);
      return false;
    }

    try {
      const itemsToProcess = [...queueItems];
      const itemIdsToProcess = itemsToProcess.map(item => item.id);

      // the API client resolves failed writes (network errors and 4xx/5xx alike) instead of rejecting,
      // so the items stay queued unless the response says they made it
      const result = await action(itemsToProcess);
      if (!result?.error) {
        if (isOnline.value) {
          clearQueueItems(itemQueueType, itemIdsToProcess);
        }
        return true;
      }

      console.log(`Failed to write queue items of type ${itemQueueType}; keeping them queued`);
      failedWriteInRun = true;

      // a rejected request says nothing about which item caused it, so send them one by one;
      // otherwise a single item the server will never accept would hold back all the others
      if (itemsToProcess.length > 1 && isRejection(result.error)) {
        for (const item of itemsToProcess) {
          const itemResult = await action([item]);
          if (!itemResult?.error && isOnline.value) {
            clearQueueItems(itemQueueType, [item.id]);
          }
        }
      }
    }
    catch (error) {
      console.log(`Error processing queue items of type ${itemQueueType}:`, error);
      clearQueueItems(itemQueueType);
      return false;
    }

    return true;
  }

  async function process() {
    if (queueEmpty.value) {
      queue.lastUpdate = Date.now();
      hasFailedWrites.value = false;
      return;
    }

    const data = await getList();
    if (!data) {
      return;
    }
    checkUpdateState(data);
    failedWriteInRun = false;

    // We send each bulk request one at a time, since the backend may merge items
    // "failures" here refers to an actual error, rather than failing to reach the backend
    let failures = 0;
    if (!(await processQueueItems(items => api.shopping.items.deleteMany(items), "delete"))) failures++;
    if (!(await processQueueItems(items => api.shopping.items.updateMany(items), "update"))) failures++;
    if (!(await processQueueItems(items => api.shopping.items.createMany(items), "create"))) failures++;

    // If we're online with no failed writes, or the queue is empty, the queue is fully processed, so we're up to date
    // Otherwise, if all three queue processes failed, we've already reset the queue, so we need to reset the date
    hasFailedWrites.value = failedWriteInRun;
    if ((isOnline.value && !failedWriteInRun) || queueEmpty.value || failures === 3) {
      queue.lastUpdate = Date.now();
    }
  }

  return {
    getList,
    createItem,
    updateItem,
    deleteItem,
    process,
    hasFailedWrites,

    __testing__: {
      queue,
      clearQueueItems,
      createEmptyQueue,
    },
  };
}
