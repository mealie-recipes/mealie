import { useLocalStorage } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { ShoppingListItemOut } from "~/lib/api/types/group";

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
  const queue = storage.value[shoppingListId] ||= { create: [], update: [], delete: [], lastUpdate: Date.now()};

  function removeFromCreate(item: ShoppingListItemOut): boolean {
    const index = queue.create.findIndex(i => i.id === item.id);
    if (index == -1) {
      return false;
    }

    queue.create.splice(index, 1);
    return true;
  }

  function removeFromUpdate(item: ShoppingListItemOut): boolean {
    const index = queue.update.findIndex(i => i.id === item.id);
    if (index == -1) {
      return false;
    }

    queue.update.splice(index, 1);
    return true;
  }

  function removeFromDelete(item: ShoppingListItemOut): boolean {
    const index = queue.delete.findIndex(i => i.id === item.id);
    if (index == -1) {
      return false;
    }

    queue.delete.splice(index, 1);
    return true;
  }

  function createItem(item: ShoppingListItemOut) {
    removeFromCreate(item);
    queue.create.push(item);
  }

  function updateItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromCreate(item);
    if (removedFromCreate) {
      // this item hasn't been created yet, so we don't need to update it
      queue.create.push(item);
      return;
    }

    removeFromUpdate(item);
    queue.update.push(item);
  }

  function deleteItem(item: ShoppingListItemOut) {
    const removedFromCreate = removeFromCreate(item);
    if (removedFromCreate) {
      // this item hasn't been created yet, so we don't need to delete it
      return;
    }

    removeFromUpdate(item);
    removeFromDelete(item);
    queue.delete.push(item);
  }

  function getQueueItems(itemQueueType: ItemQueueType) {
    return queue[itemQueueType];
  }

  function clearQueueItems(itemQueueType: ItemQueueType | "all") {
    switch (itemQueueType) {
      case "create":
        queue.create = [];
        break;
      case "update":
        queue.update = [];
        break;
      case "delete":
        queue.delete = [];
        break;
      case "all":
        queue.create = [];
        queue.update = [];
        queue.delete = [];
        break;
    }
  }

  async function processQueueItems(
    action: (items: ShoppingListItemOut[]) => Promise<any>,
    itemQueueType: ItemQueueType,
  ) {
    const items = getQueueItems(itemQueueType);
    if (!items.length) {
      return;
    }

    await action(items)
      .then((response) => {
        // TODO: is there a better way of checking for network errors?
        if (!response?.error?.includes("Network Error")) {
          clearQueueItems(itemQueueType);
        }
      });
  }

  async function process() {
    if(
      !queue.create.length &&
      !queue.update.length &&
      !queue.delete.length
    ) {
      // The queue is empty, so there's no need to do anything
      queue.lastUpdate = Date.now();
      return;
    }

    const { data } = await api.shopping.lists.getOne(shoppingListId);
    if (!data) {
      // We can't fetch the shopping list, so we can't do anything.
      // Additionally, by returning early, we don't update the "lastUpdate" time.
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

    queue.lastUpdate = Date.now();
  }

  return {
    createItem,
    updateItem,
    deleteItem,
    process,
  };
}
