import * as vuecore from "@vueuse/core";
import { beforeEach, describe, expect, test, vi } from "vitest";
import type { ShoppingListQueue } from "../use-shopping-list-item-actions";
import { useShoppingListItemActions } from "../use-shopping-list-item-actions";
import { MOCK_ITEM, MOCK_SHOPPING_LIST } from "./mocks";

const getOne = vi.fn().mockResolvedValue({ data: MOCK_SHOPPING_LIST });

const deleteMany = vi.fn().mockImplementation(async () => { });
const updateMany = vi.fn().mockImplementation(async () => { });
const createMany = vi.fn().mockImplementation(async () => { });

vi.mock("@vueuse/core", { spy: true });
const isOnline = ref(true);
const storedValue = ref<{ [key: string]: ShoppingListQueue } | undefined>(undefined);
vi.mocked(vuecore.useOnline).mockReturnValue(isOnline);
vi.mocked(vuecore.useStorage).mockReturnValue(storedValue);

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    shopping: {
      lists: { getOne },
      items: { deleteMany, updateMany, createMany },
    },
  }),
}));

describe("useShoppingListItemActions", () => {
  const {
    getList,
    createItem,
    deleteItem,
    updateItem,
    process,
    __testing__: { queue, clearQueueItems },
  } = useShoppingListItemActions("list_id");

  beforeEach(() => {
    vi.clearAllMocks();
    isOnline.value = true;
    storedValue.value = undefined;
    clearQueueItems("all");
  });

  test("getList returns a shopping list", async () => {
    const list = await getList();
    expect(list).toBe(MOCK_SHOPPING_LIST);
  });
  test("create item creates an item", () => {
    createItem(MOCK_ITEM);
    expect(queue.create.includes(MOCK_ITEM));
  });
  describe("updateItem", () => {
    test("update item updates an item", () => {
      updateItem(MOCK_ITEM);
      expect(queue.update).include(MOCK_ITEM);
    });
    test("ignores a newly created item", () => {
      const updatedItem = { ...MOCK_ITEM, quantity: 2000 };
      createItem(MOCK_ITEM);
      updateItem(updatedItem);
      expect(queue.update).not.include(MOCK_ITEM);
      expect(queue.create).not.include(MOCK_ITEM);
      expect(queue.create).include(updatedItem);
    });
  });
  describe("deleteItem", () => {
    test("delete item deletes an item", () => {
      deleteItem(MOCK_ITEM);
      expect(queue.delete).include(MOCK_ITEM);
    });
    test("undoes a newly created item", () => {
      createItem(MOCK_ITEM);
      deleteItem(MOCK_ITEM);
      expect(queue.delete).not.include(MOCK_ITEM);
      expect(queue.create).not.include(MOCK_ITEM);
    });
  });
  describe("process processes the queue", () => {
    test("normally", async () => {
      const updatedItem = { ...MOCK_ITEM, id: "update" };
      const createdItem = { ...MOCK_ITEM, id: "create" };
      const deletedItem = { ...MOCK_ITEM, id: "delete" };

      updateItem(updatedItem);
      createItem(createdItem);
      deleteItem(deletedItem);

      await process();
      expect(queue.update).not.include(updatedItem);
      expect(queue.create).not.include(createdItem);
      expect(queue.delete).not.include(deletedItem);
    });
    test("clears the queue if there was an error merging", async () => {
      updateMany.mockThrowOnce("💥 Woe, exception be upon ye 💥");
      createMany.mockThrowOnce("💥 Woe, exception be upon ye 💥");
      deleteMany.mockThrowOnce("💥 Woe, exception be upon ye 💥");

      const updatedItem = { ...MOCK_ITEM, id: "update" };
      const createdItem = { ...MOCK_ITEM, id: "create" };
      const deletedItem = { ...MOCK_ITEM, id: "delete" };

      updateItem(updatedItem);
      createItem(createdItem);
      deleteItem(deletedItem);

      await process();
      expect(queue.update).not.include(updatedItem);
      expect(queue.create).not.include(createdItem);
      expect(queue.delete).not.include(deletedItem);
    });
    test("doesn't clear the queue if offline", async () => {
      isOnline.value = false;

      const updatedItem = { ...MOCK_ITEM, id: "update" };
      const createdItem = { ...MOCK_ITEM, id: "create" };
      const deletedItem = { ...MOCK_ITEM, id: "delete" };

      updateItem(updatedItem);
      createItem(createdItem);
      deleteItem(deletedItem);

      await process();
      expect(queue.update).include(updatedItem);
      expect(queue.create).include(createdItem);
      expect(queue.delete).include(deletedItem);
    });
    test("doesn't do anything if the queue is empty", async () => {
      await process();
      expect(updateMany).not.toHaveBeenCalled();
      expect(createMany).not.toHaveBeenCalled();
      expect(deleteMany).not.toHaveBeenCalled();
    });
    test("doesn't do anything if we can't find the list", async () => {
      getOne.mockResolvedValue({ data: undefined });
      const updatedItem = { ...MOCK_ITEM, id: "update" };
      const createdItem = { ...MOCK_ITEM, id: "create" };
      const deletedItem = { ...MOCK_ITEM, id: "delete" };

      updateItem(updatedItem);
      createItem(createdItem);
      deleteItem(deletedItem);

      await process();
      expect(updateMany).not.toHaveBeenCalled();
      expect(createMany).not.toHaveBeenCalled();
      expect(deleteMany).not.toHaveBeenCalled();
    });
  });
  describe("getQueue", () => {
    test("fetches from local storage if available", () => {
      const { queue, createEmptyQueue } = useShoppingListItemActions("list_id").__testing__;
      expect(queue).not.toEqual(createEmptyQueue);
    });
  });
});
