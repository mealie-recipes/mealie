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
    hasFailedWrites,
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
    describe("when a write fails", () => {
      // same shape as request.safe in api-client.ts: failed writes resolve rather than reject
      function failedResponse(status?: number) {
        const error = Object.assign(new Error("request failed"), status ? { response: { status } } : {});
        return { response: null, error, data: null };
      }

      test.each([
        ["a network error", undefined],
        ["a 400", 400],
        ["a 401", 401],
        ["a 404", 404],
        ["a 422", 422],
        ["a 500", 500],
        ["a 503", 503],
      ])("keeps all three queues after %s", async (_, status) => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        deleteMany.mockResolvedValueOnce(failedResponse(status));
        updateMany.mockResolvedValueOnce(failedResponse(status));
        createMany.mockResolvedValueOnce(failedResponse(status));

        const updatedItem = { ...MOCK_ITEM, id: "update" };
        const createdItem = { ...MOCK_ITEM, id: "create" };
        const deletedItem = { ...MOCK_ITEM, id: "delete" };

        updateItem(updatedItem);
        createItem(createdItem);
        deleteItem(deletedItem);

        await process();
        expect(queue.update.map(item => item.id)).toEqual(["update"]);
        expect(queue.create.map(item => item.id)).toEqual(["create"]);
        expect(queue.delete.map(item => item.id)).toEqual(["delete"]);
      });

      test("only keeps the queue whose write failed", async () => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        updateMany.mockResolvedValueOnce(failedResponse(500));
        createMany.mockResolvedValueOnce({ response: { status: 201 }, error: null, data: {} });

        updateItem({ ...MOCK_ITEM, id: "update" });
        createItem({ ...MOCK_ITEM, id: "create" });

        await process();
        expect(queue.update.map(item => item.id)).toEqual(["update"]);
        expect(queue.create).toEqual([]);
      });

      test("sends the kept items again on the next run, then clears them", async () => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        updateMany.mockResolvedValueOnce(failedResponse(503));
        updateMany.mockResolvedValueOnce({ response: { status: 200 }, error: null, data: {} });

        updateItem({ ...MOCK_ITEM, id: "update" });

        await process();
        expect(queue.update.map(item => item.id)).toEqual(["update"]);

        await process();
        expect(updateMany).toHaveBeenCalledTimes(2);
        expect(updateMany.mock.calls[1]?.[0].map((item: { id: string }) => item.id)).toEqual(["update"]);
        expect(queue.update).toEqual([]);
      });

      test("treats the queue like an offline one, so its age keeps counting", async () => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        updateMany.mockResolvedValueOnce(failedResponse(500));

        updateItem({ ...MOCK_ITEM, id: "update" });
        queue.lastUpdate = 1000;

        await process();
        expect(queue.lastUpdate).toBe(1000);
      });

      test("sends the items one by one after a rejection, so one bad item can't hold back the others", async () => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        const ok = { response: { status: 200 }, error: null, data: {} };
        updateMany.mockResolvedValueOnce(failedResponse(422));
        updateMany.mockResolvedValueOnce(ok);
        updateMany.mockResolvedValueOnce(failedResponse(422));

        updateItem({ ...MOCK_ITEM, id: "good" });
        updateItem({ ...MOCK_ITEM, id: "bad" });

        await process();
        expect(updateMany).toHaveBeenCalledTimes(3);
        expect(queue.update.map(item => item.id)).toEqual(["bad"]);
      });

      test.each([500, 503, 401, 429, undefined])("doesn't split the request after a temporary failure (%s)", async (status) => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        updateMany.mockResolvedValueOnce(failedResponse(status));

        updateItem({ ...MOCK_ITEM, id: "a" });
        updateItem({ ...MOCK_ITEM, id: "b" });

        await process();
        expect(updateMany).toHaveBeenCalledTimes(1);
        expect(queue.update).toHaveLength(2);
      });

      test("reports failed writes until a run saves everything", async () => {
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
        updateMany.mockResolvedValueOnce(failedResponse(500));
        updateMany.mockResolvedValueOnce(failedResponse(500));

        updateItem({ ...MOCK_ITEM, id: "update" });
        await process();
        expect(hasFailedWrites.value).toBe(true);

        await process();
        expect(hasFailedWrites.value).toBe(true);

        await process();
        expect(hasFailedWrites.value).toBe(false);
      });

      test("keeps the local change visible in getList", async () => {
        const checkedItem = { ...MOCK_ITEM, id: "server-item", checked: true, updatedAt: "200" };
        getOne.mockImplementation(async () => ({
          data: { ...MOCK_SHOPPING_LIST, listItems: [{ ...MOCK_ITEM, id: "server-item", checked: false, updatedAt: "100" }] },
        }));
        updateMany.mockResolvedValueOnce(failedResponse(500));

        updateItem(checkedItem);
        await process();

        const list = await getList();
        expect(list?.listItems?.find(item => item.id === "server-item")?.checked).toBe(true);
        getOne.mockReset();
        getOne.mockResolvedValue({ data: MOCK_SHOPPING_LIST });
      });
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
