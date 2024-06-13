import { useLocalStorage } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { ShoppingListItemOut } from "~/lib/api/types/group";

const localStorageKey = "shopping-list-queue";

type QueueType = "create" | "update" | "delete";

interface ShoppingListQueue {
  create: ShoppingListItemOut[];
  update: ShoppingListItemOut[];
  delete: ShoppingListItemOut[];
}

interface Storage {
  [key: string]: ShoppingListQueue;
}

export function useShoppingListItemActions(shoppingListId: string) {
  const api = useUserApi();
  const storage = useLocalStorage(localStorageKey, {} as Storage, { deep: true });
  const queue = storage.value[shoppingListId] ||= { create: [], update: [], delete: [] };

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

  function getQueue(queueType: QueueType) {
    return queue[queueType];
  }

  function clearQueue(queueType: QueueType) {
    switch (queueType) {
      case "create":
        queue.create = [];
        break;
      case "update":
        queue.update = [];
        break;
      case "delete":
        queue.delete = [];
        break;
    }
  }

  async function processQueueItems(
    action: (items: ShoppingListItemOut[]) => Promise<any>,
    queueType: QueueType,
  ) {
    const items = getQueue(queueType);
    if (!items.length) {
      return;
    }

    await action(items)
      .then((response) => {
        // TODO: is there a better way of checking for network errors?
        if (!response.error.includes("Network Error")) {
          clearQueue(queueType);
        }
      });
  }

  async function process() {
    // we send each bulk request one at a time, since the backend may merge items
    await processQueueItems((items) => api.shopping.items.deleteMany(items), "delete");
    await processQueueItems((items) => api.shopping.items.updateMany(items), "update");
    await processQueueItems((items) => api.shopping.items.createMany(items), "create");
  }

  return {
    createItem,
    updateItem,
    deleteItem,
    process,
  };
}
