import { computed, ref } from "@nuxtjs/composition-api";
import { useLocalStorage } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { ShoppingListItemOut } from "~/lib/api/types/group";
import { RequestResponse } from "~/lib/api/types/non-generated";

const localStorageKey = "shopping-list-queue";
const queueTimeout = 5 * 60 * 1000;  // 5 minutes

type ItemQueueType = "create" | "update" | "delete";

interface ShoppingListQueue {
  create: ShoppingListItemOut[];
  update: ShoppingListItemOut[];
  delete: ShoppingListItemOut[];

  lastUpdate: number;
}

interface Storage {
  [key: string]: ShoppingListQueue;
}

export function useShoppingListItemActions(shoppingListId: string) {
  const api = useUserApi();
  const storage = useLocalStorage(localStorageKey, {} as Storage, { deep: true });
  const queue = getQueue();
  const queueEmpty = computed(() => !queue.create.length && !queue.update.length && !queue.delete.length);
  if (queueEmpty.value) {
    queue.lastUpdate = Date.now();
  }

  const isOffline = ref(false);

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
    return { create: [], update: [], delete: [], lastUpdate: Date.now() };
  }

  function getQueue(): ShoppingListQueue {
    try {
      const queue = storage.value[shoppingListId];
      if (!isValidQueueObject(queue)) {
        return createEmptyQueue();
      } else {
        return queue;
      }
    } catch {
      return createEmptyQueue();
    }
  }

  function removeFromQueue(queue: ShoppingListItemOut[], item: ShoppingListItemOut): boolean {
    const index = queue.findIndex(i => i.id === item.id);
    if (index === -1) {
      return false;
    }

    queue.splice(index, 1);
    return true;
  }

  async function getList() {
    const response = await api.shopping.lists.getOne(shoppingListId);
    handleResponse(response);
    return response.data;
  }

  function createItem(item: ShoppingListItemOut) {
    removeFromQueue(queue.create, item);
    queue.create.push(item);
  }

  function updateItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromQueue(queue.create, item);
    if (removedFromCreate) {
      // this item hasn't been created yet, so we don't need to update it
      queue.create.push(item);
      return;
    }

    removeFromQueue(queue.update, item);
    queue.update.push(item);
  }

  function deleteItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromQueue(queue.create, item);
    if (removedFromCreate) {
      // this item hasn't been created yet, so we don't need to delete it
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
    if (itemQueueType === "all") {
      queue.lastUpdate = Date.now();
    }

    // Set the storage value explicitly so changes are saved in the browser.
    storage.value[shoppingListId] = { ...queue };
  }

  /**
   * Handles the response from the backend and sets the isOffline flag if necessary.
   */
  function handleResponse(response: RequestResponse<any>) {
    // TODO: is there a better way of checking for network errors?
    isOffline.value = response?.response?.status === undefined;
  }

  /**
   * Processes the queue items and returns whether the processing was successful.
   */
  async function processQueueItems(
    action: (items: ShoppingListItemOut[]) => Promise<any>,
    itemQueueType: ItemQueueType,
  ): Promise<boolean> {
    let queueItems: ShoppingListItemOut[];
    try {
      queueItems = getQueueItems(itemQueueType);
      if (!queueItems.length) {
        return true;
      }
    } catch (error) {
      console.log(`Error fetching queue items of type ${itemQueueType}:`, error);
      clearQueueItems(itemQueueType);
      return false;
    }

    try {
      const itemsToProcess = [...queueItems];
      await action(itemsToProcess)
        .then((response) => {
          handleResponse(response);
          if (!isOffline.value) {
            clearQueueItems(itemQueueType, itemsToProcess.map(item => item.id));
          }
        });
    } catch (error) {
      console.log(`Error processing queue items of type ${itemQueueType}:`, error);
      clearQueueItems(itemQueueType);
      return false;
    }

    return true;
  }

  async function process() {
    if(
      !queue.create.length &&
      !queue.update.length &&
      !queue.delete.length
    ) {
      return;
    }

    const data = await getList();
    if (!data) {
      return;
    }

    const cutoffDate = new Date(queue.lastUpdate + queueTimeout).toISOString();
    if (data.updateAt && data.updateAt > cutoffDate) {
      // If the queue is too far behind the shopping list to reliably do updates, we clear the queue
      clearQueueItems("all");
      return;
    }

    // We send each bulk request one at a time, since the backend may merge items
    // "failures" here refers to an actual error, rather than failing to reach the backend
    let failures = 0;
    await processQueueItems((items) => api.shopping.items.deleteMany(items), "delete") ? null : failures++;
    await processQueueItems((items) => api.shopping.items.updateMany(items), "update") ? null : failures++;
    await processQueueItems((items) => api.shopping.items.createMany(items), "create") ? null : failures++;

    // If we're online, the queue is fully processed, so we're up to date
    // Otherwise, if all three queue processes failed, we've already reset the queue, so we need to reset the date
    if (!isOffline.value || failures === 3) {
      queue.lastUpdate = Date.now();
    }
  }

  return {
    isOffline,
    getList,
    createItem,
    updateItem,
    deleteItem,
    process,
  };
}
