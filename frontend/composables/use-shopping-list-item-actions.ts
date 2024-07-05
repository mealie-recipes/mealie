import { computed, ref } from "@nuxtjs/composition-api";
import { useLocalStorage } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { ShoppingListItemOut } from "~/lib/api/types/group";

const localStorageKey = "shopping-list-queue";
const queueTimeout = 48 * 60 * 60 * 1000;  // 48 hours

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
  const queue = storage.value[shoppingListId] ||= { create: [], update: [], delete: [], lastUpdate: Date.now()};
  const queueEmpty = computed(() => !queue.create.length && !queue.update.length && !queue.delete.length);
  if (queueEmpty.value) {
    queue.lastUpdate = Date.now();
  }

  const isOffline = ref(false);

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

    // Set the storage value explicitly so changes are saved in the browser.
    storage.value[shoppingListId] = { ...queue };
  }

  /**
   * Handles the response from the backend and sets the isOffline flag if necessary.
   */
  function handleResponse(response: any) {
    // TODO: is there a better way of checking for network errors?
    isOffline.value = response.error?.message?.includes("Network Error") || false;
  }

  async function processQueueItems(
    action: (items: ShoppingListItemOut[]) => Promise<any>,
    itemQueueType: ItemQueueType,
  ) {
    const queueItems = getQueueItems(itemQueueType);
    if (!queueItems.length) {
      return;
    }

    const itemsToProcess = [...queueItems];
    await action(itemsToProcess)
      .then((response) => {
        handleResponse(response);
        if (!isOffline.value) {
          clearQueueItems(itemQueueType, itemsToProcess.map(item => item.id));
        }
      });
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
    } else {
      // We send each bulk request one at a time, since the backend may merge items
      await processQueueItems((items) => api.shopping.items.deleteMany(items), "delete");
      await processQueueItems((items) => api.shopping.items.updateMany(items), "update");
      await processQueueItems((items) => api.shopping.items.createMany(items), "create");
    }

    // If we're online, the queue is fully processed, so we're up to date
    if (!isOffline.value) {
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
