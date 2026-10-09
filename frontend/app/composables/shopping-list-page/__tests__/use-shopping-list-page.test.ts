import { beforeEach, describe, expect, test, vi } from "vitest";
import { MOCK_ITEM, MOCK_SHOPPING_LIST } from "../sub-composables/__tests__/mocks";
import { useShoppingListPage } from "../use-shopping-list-page";
import * as vue from "vue";

const addRecipes = vi.fn().mockResolvedValue({ data: true });
const removeRecipe = vi.fn().mockResolvedValue(({ data: true }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    shopping: { lists: { addRecipes, removeRecipe } },
  }),
}));

const sorting = {
  groupAndSortListItemsByFood: vi.fn(),
  sortListItems: vi.fn(),
  updateItemsByLabel: vi.fn(),
};
vi.mock("../sub-composables/use-shopping-list-sorting", () => ({
  useShoppingListSorting: () => sorting,
}));

const data = {
  refresh: vi.fn().mockImplementation(fn => fn()),
  startPolling: vi.fn(),
  stopPolling: vi.fn(),
};
vi.mock("../sub-composables/use-shopping-list-data", () => ({
  useShoppingListData: () => data,
}));

vi.mock("../sub-composables/use-shopping-list-labels", () => ({
  useShoppingListLabels: () => ({ getLabelColor: vi.fn() }),
}));

const mockCopyListItems = vi.fn();
vi.mock("../sub-composables/use-shopping-list-copy", () => ({
  useShoppingListCopy: () => ({ copyListItems: mockCopyListItems }),
}));

const crud = {
  listItemFactory: vi.fn(),
  checkAllItems: vi.fn(),
  uncheckAllItems: vi.fn(),
  deleteCheckedItems: vi.fn(),
  saveListItem: vi.fn(),
  deleteListItem: vi.fn(),
  deleteListItems: vi.fn(),
  createListItem: vi.fn(),
  updateUncheckedListItems: vi.fn(),
  updateLabelOrder: vi.fn(),
  cancelLabelOrder: vi.fn(),
  saveLabelOrder: vi.fn(),
  toggleReorderLabelsDialog: vi.fn(),
};
vi.mock("../sub-composables/use-shopping-list-crud", () => ({
  useShoppingListCrud: () => crud,
}));

vi.mock("vue", { spy: true });
vi.mocked(vue.onUnmounted).mockImplementation(fn => fn());
vi.mocked(vue.onMounted).mockImplementation(fn => fn());

describe("useShoppingListPage", () => {
  const {
    shoppingList,
    state,
    itemsByLabel,
    preserveItemOrder,
    updateIndexUncheckedByLabel,
    copyListItems,
    openCheckAll,
    openUncheckAll,
    openDeleteChecked,
    checkAll,
    uncheckAll,
    deleteChecked,
    toggleReorderLabelsDialog,
    saveLabelOrder,
    refresh,
  } = useShoppingListPage("list_id");

  beforeEach(() => {
    vi.clearAllMocks();
    state.checkAllDialog = false;
    state.uncheckAllDialog = false;
    state.deleteCheckedDialog = false;
    preserveItemOrder.value = false;
    itemsByLabel.value = { myKey: [] };
    shoppingList.value = {
      ...MOCK_SHOPPING_LIST,
      listItems: [
        MOCK_ITEM,
        { ...MOCK_ITEM, checked: true },
      ],
    };
  });
  describe("openCheckAll", () => {
    test("opens the dialog", () => {
      openCheckAll();
      expect(state.checkAllDialog).toBe(true);
    });
    test("skips the dialog if there's nothing to check", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          { ...MOCK_ITEM, checked: true },
        ],
      };
      openCheckAll();
      expect(state.checkAllDialog).toBe(false);
    });
  });
  describe("openUncheckAll", () => {
    test("opens the dialog", () => {
      openUncheckAll();
      expect(state.uncheckAllDialog).toBe(true);
    });
    test("skips the dialog if there's nothing to uncheck", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
        ],
      };
      openUncheckAll();
      expect(state.uncheckAllDialog).toBe(false);
    });
  });
  describe("openDeleteChecked", () => {
    test("opens the dialog", () => {
      openDeleteChecked();
      expect(state.deleteCheckedDialog).toBe(true);
    });
    test("skips the dialog if there's nothing to delete", () => {
      shoppingList.value = {
        ...MOCK_SHOPPING_LIST,
        listItems: [
          MOCK_ITEM,
        ],
      };
      openDeleteChecked();
      expect(state.deleteCheckedDialog).toBe(false);
    });
  });
  describe("checkAll", () => {
    test("closes the dialog", () => {
      state.checkAllDialog = true;
      checkAll();
      expect(state.checkAllDialog).toBe(false);
    });
    test("calls the crud action", () => {
      checkAll();
      expect(crud.checkAllItems).toHaveBeenCalled();
    });
  });
  describe("uncheckAll", () => {
    test("closes the dialog", () => {
      state.uncheckAllDialog = true;
      uncheckAll();
      expect(state.uncheckAllDialog).toBe(false);
    });
    test("calls the crud action", () => {
      uncheckAll();
      expect(crud.uncheckAllItems).toHaveBeenCalled();
    });
  });
  describe("deleteChecked", () => {
    test("closes the dialog", () => {
      state.deleteCheckedDialog = true;
      deleteChecked();
      expect(state.deleteCheckedDialog).toBe(false);
    });
    test("calls the crud action", () => {
      deleteChecked();
      expect(crud.deleteCheckedItems).toHaveBeenCalled();
    });
  });
  describe("copyListItems", () => {
    test("copys list items", () => {
      copyListItems("markdown");
      expect(mockCopyListItems).toHaveBeenCalled();
    });
  });
  describe("toggleReorderLabelsDialog", () => {
    test("toggles the dialog", () => {
      toggleReorderLabelsDialog();
      expect(crud.toggleReorderLabelsDialog).toHaveBeenCalled();
    });
  });
  describe("saveLabelOrder", () => {
    test("saves label order", async () => {
      crud.saveLabelOrder.mockImplementation(fn => fn());
      sorting.updateItemsByLabel.mockReturnValue({ myKey2: [] });
      await saveLabelOrder();
      expect(crud.saveLabelOrder).toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey2: [] });
    });
    test("doesn't delete label order if something goes wrong", async () => {
      crud.saveLabelOrder.mockImplementation(fn => fn());
      sorting.updateItemsByLabel.mockReturnValue(undefined);
      await saveLabelOrder();
      expect(crud.saveLabelOrder).toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey: [] });
    });
  });
  describe("refresh", () => {
    test("updates list item order", () => {
      sorting.updateItemsByLabel.mockReturnValue({ myKey2: [] });
      refresh();
      expect(sorting.groupAndSortListItemsByFood).toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey2: [] });
    });
    test("preserves user item order", () => {
      preserveItemOrder.value = true;
      sorting.updateItemsByLabel.mockReturnValue({ myKey2: [] });
      refresh();
      expect(sorting.sortListItems).toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey2: [] });
    });
    test("doesn't overwrite list items if something goes wrong", () => {
      sorting.updateItemsByLabel.mockReturnValue(undefined);
      refresh();
      expect(sorting.groupAndSortListItemsByFood).toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey: [] });
    });
    test("doesn't panic if shopping list doesn't exist", () => {
      shoppingList.value = null;
      sorting.updateItemsByLabel.mockReturnValue({ myKey2: [] });
      refresh();
      expect(sorting.groupAndSortListItemsByFood).not.toHaveBeenCalled();
      expect(itemsByLabel.value).toEqual({ myKey: [] });
    });
  });
  describe("updateIndexUncheckedByLabel", () => {
    test("updates items", () => {
      updateIndexUncheckedByLabel("myKey", []);
      expect(crud.updateUncheckedListItems).toHaveBeenCalled();
    });
    test("doesn't panic if key doesn't exist", () => {
      updateIndexUncheckedByLabel("myKey2", []);
      expect(crud.updateUncheckedListItems).not.toHaveBeenCalled();
    });
  });
  describe("Lifecycle hooks", () => {
    test("starts polling on mount", async () => {
      useShoppingListPage("list_id");
      expect(data.startPolling).toHaveBeenCalled();
    });
    test("stops polling on unmount", async () => {
      useShoppingListPage("list_id");
      expect(data.stopPolling).toHaveBeenCalled();
    });
  });
});
