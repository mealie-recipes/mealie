import { beforeEach, describe, expect, test, vi } from "vitest";
import { useShoppingListCrud } from "../use-shopping-list-crud";
import { useShoppingListState } from "../use-shopping-list-state";
import { MOCK_ITEM, MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3, MOCK_SHOPPING_LIST } from "./mocks";

const mockUpdate = vi.fn();
const mockRefresh = vi.fn();
const getOne = vi.fn().mockResolvedValue({ data: MOCK_SHOPPING_LIST });
const updateLabelSettings = vi.fn().mockResolvedValue({ data: MOCK_SHOPPING_LIST });
const deleteMany = vi.fn();
const updateMany = vi.fn();
const createMany = vi.fn();
// const consoleError = vi.spyOn(console, "error");
// vi.spyOn(window, "setInterval").mockImplementation((fn) => {
//   new Promise(resolve => setTimeout(resolve, 1)).then(() => fn());
//   return "TIMEOUT" as any;
// });
// const mockClearInterval = vi.spyOn(window, "clearInterval");

// vi.mock("@vueuse/core", { spy: true });
vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    shopping: {
      lists: { getOne, updateLabelSettings },
      items: { deleteMany, updateMany, createMany },
    },
  }),
}));

// const mockUseOnline = vi.mocked(vuecore.useOnline);
// const mockUseIdle = vi.mocked(vuecore.useIdle);

describe("use-shopping-list-crud", () => {
  const isOnline = shallowRef(true);
  const isIdle = shallowRef(false);
  // mockUseOnline.mockReturnValue(isOnline);
  // mockUseIdle.mockReturnValue({ idle: isIdle } as vuecore.UseIdleReturn);

  const list = { ...MOCK_SHOPPING_LIST, id: "1" };
  const { shoppingList, loadingCounter, listItems, sortCheckedItems } = useShoppingListState();
  const shoppingListItemActions = {
    getList: vi.fn(),
    createItem: vi.fn(),
    updateItem: vi.fn(),
    deleteItem: vi.fn(),
    process: vi.fn(),
  };

  const {
    createListItemData,
    localLabels,
    checkAllItems,
    uncheckAllItems,
    deleteCheckedItems,
    saveListItem,
    deleteListItem,
    createListItem,
    updateLabelOrder,
    cancelLabelOrder,
    saveLabelOrder,
    toggleReorderLabelsDialog,
  } = useShoppingListCrud(
    shoppingList,
    loadingCounter,
    listItems,
    shoppingListItemActions,
    mockRefresh,
    sortCheckedItems,
    mockUpdate,
  );

  beforeEach(() => {
    shoppingList.value = list;
    loadingCounter.value = 0;
    isOnline.value = true;
    isIdle.value = false;
    mockUpdate.mockClear();
    mockRefresh.mockClear();
    shoppingListItemActions.updateItem.mockClear();
    shoppingListItemActions.deleteItem.mockClear();
    shoppingListItemActions.createItem.mockClear();
    shoppingListItemActions.process.mockClear();
    shoppingListItemActions.getList.mockClear();
    updateLabelSettings.mockClear();
    // mockClearInterval.mockClear();
    // consoleError.mockClear();
  });

  describe("checkAllItems", () => {
    test("checks items", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, checked: true },
        ],
      };
      checkAllItems();
      expect(mockRefresh).toHaveBeenCalled();
    });
    test("doesn't refresh if nothing changed", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          { ...MOCK_ITEM, checked: true },
          { ...MOCK_ITEM, checked: true },
        ],
      };
      checkAllItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      checkAllItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
  });
  describe("uncheckAllItems", () => {
    test("unchecks items", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, checked: true },
        ],
      };
      uncheckAllItems();
      expect(mockRefresh).toHaveBeenCalled();
    });
    test("doesn't refresh if nothing changed", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      uncheckAllItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      uncheckAllItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
  });
  describe("deleteCheckedItems", () => {
    test("unchecks items", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, checked: true },
        ],
      };
      deleteCheckedItems();
      expect(mockRefresh).toHaveBeenCalled();
    });
    test("doesn't refresh if nothing changed", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      deleteCheckedItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      deleteCheckedItems();
      expect(mockRefresh).not.toHaveBeenCalled();
    });
  });
  describe("saveListItem", () => {
    test("saves list item", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      saveListItem(MOCK_ITEM);
      expect(shoppingListItemActions.updateItem).toHaveBeenCalledWith(MOCK_ITEM);
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      saveListItem(MOCK_ITEM);
      expect(shoppingListItemActions.updateItem).not.toHaveBeenCalled();
    });
  });
  describe("delete list item", () => {
    test("deletes list item", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      deleteListItem(MOCK_ITEM);
      expect(shoppingListItemActions.deleteItem).toHaveBeenCalledWith(MOCK_ITEM);
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      deleteListItem(MOCK_ITEM);
      expect(shoppingListItemActions.deleteItem).not.toHaveBeenCalled();
    });
  });
  describe("create list item", () => {
    test("creates list item", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      createListItemData.value.foodId = "foodId";
      createListItem();
      expect(shoppingListItemActions.createItem).toHaveBeenCalled();
    });
    test("doesn't create empty items", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      createListItem();
      expect(shoppingListItemActions.createItem).not.toHaveBeenCalled();
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      createListItem();
      expect(shoppingListItemActions.createItem).not.toHaveBeenCalled();
    });
  });
  describe("update label order", () => {
    test("updates label order", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      const labelSettings = [MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3];
      updateLabelOrder(labelSettings);
      expect(localLabels.value).toEqual(labelSettings);
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      const labelSettings = [MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3];
      updateLabelOrder(labelSettings);
      expect(localLabels).not.toEqual(labelSettings);
    });
  });
  describe("cancel label order", () => {
    test("cancels label order", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      cancelLabelOrder();
      expect(loadingCounter.value).toBe(-1);
      expect(localLabels.value).toEqual(shoppingList.value.labelSettings);
    });
    test("doesn't panic if shopping list is null", () => {
      shoppingList.value = null;
      cancelLabelOrder();
      expect(loadingCounter.value).toBe(-1);
      expect(localLabels.value).not.toEqual((shoppingList.value as any)?.labelSettings);
    });
  });
  describe("save label order", () => {
    test("saves label order", async () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
          MOCK_ITEM,
        ],
      };
      const labelSettings = [MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3];
      updateLabelOrder(labelSettings);
      await saveLabelOrder(mockUpdate);
      expect(updateLabelSettings).toHaveBeenCalled();
      expect(mockUpdate).toHaveBeenCalled();
    });
    test("doesn't panic if shopping list is null", async () => {
      shoppingList.value = null;
      const labelSettings = [MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3];
      updateLabelOrder(labelSettings);
      await saveLabelOrder(mockUpdate);
      expect(updateLabelSettings).not.toHaveBeenCalled();
      expect(mockUpdate).not.toHaveBeenCalled();
    });
  });
  describe("toggle label order dialog", () => {
    test("toggles label order dialog", async () => {
      const isOpen = ref(false);
      toggleReorderLabelsDialog(isOpen);
      expect(isOpen.value).toBe(true);
      expect(localLabels.value).toEqual(shoppingList.value?.labelSettings);
    });
  });
});
