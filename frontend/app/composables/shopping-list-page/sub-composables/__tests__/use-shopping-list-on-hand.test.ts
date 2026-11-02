import { beforeEach, describe, expect, test, vi } from "vitest";
import type { ShoppingListItemOut, ShoppingListOut } from "~/lib/api/types/household";
import { makeWrapper } from "~/tests/utils";
import { useShoppingListOnHand } from "../use-shopping-list-on-hand";
import { MOCK_ITEM, MOCK_SHOPPING_LIST } from "./mocks";

const mocks = vi.hoisted(() => ({
  addFoodsOnHand: vi.fn(),
  deleteListItems: vi.fn(),
  alert: { success: vi.fn(), info: vi.fn(), error: vi.fn() },
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    households: { addFoodsOnHand: mocks.addFoodsOnHand },
  }),
}));

vi.mock("~/composables/use-toast", () => ({
  alert: mocks.alert,
}));

function item(overrides: Partial<ShoppingListItemOut>): ShoppingListItemOut {
  return { ...MOCK_ITEM, ...overrides };
}

function deletedItemIds(): string[] {
  return mocks.deleteListItems.mock.calls.flatMap(([items]) => items.map((i: ShoppingListItemOut) => i.id));
}

describe("useShoppingListOnHand", () => {
  const shoppingList = ref<ShoppingListOut | null>(null);
  const wrapper = makeWrapper(() => useShoppingListOnHand(shoppingList, mocks.deleteListItems));

  function setItems(listItems: ShoppingListItemOut[]) {
    shoppingList.value = { ...MOCK_SHOPPING_LIST, listItems };
  }

  beforeEach(() => {
    vi.clearAllMocks();
    mocks.addFoodsOnHand.mockResolvedValue({ data: { message: "", error: false }, error: null });
  });

  test("marks the food of each checked item once and removes those items", async () => {
    setItems([
      item({ id: "a", checked: true, foodId: "food-1" }),
      item({ id: "b", checked: true, foodId: "food-1" }),
      item({ id: "c", checked: true, foodId: "food-2" }),
      item({ id: "d", checked: false, foodId: "food-3" }),
    ]);

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.addFoodsOnHand).toHaveBeenCalledExactlyOnceWith(["food-1", "food-2"]);
    expect(deletedItemIds()).toEqual(["a", "b", "c"]);
    expect(mocks.alert.success).toHaveBeenCalledExactlyOnceWith("Marked 2 foods as on hand.");
  });

  test("keeps checked items that have no food on the list", async () => {
    setItems([
      item({ id: "a", checked: true, foodId: "food-1" }),
      item({ id: "b", checked: true, foodId: undefined, note: "paper towels" }),
    ]);

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.addFoodsOnHand).toHaveBeenCalledExactlyOnceWith(["food-1"]);
    expect(deletedItemIds()).toEqual(["a"]);
    expect(mocks.alert.success).toHaveBeenCalledExactlyOnceWith(
      "Marked one food as on hand. Skipped one checked item that has no food.",
    );
  });

  test("doesn't call the API or remove anything when no checked item has a food", async () => {
    setItems([item({ id: "a", checked: true, foodId: null, note: "paper towels" })]);

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.addFoodsOnHand).not.toHaveBeenCalled();
    expect(mocks.deleteListItems).not.toHaveBeenCalled();
    expect(mocks.alert.info).toHaveBeenCalledExactlyOnceWith(
      "None of the checked items have a food, so nothing was marked as on hand.",
    );
  });

  test("does nothing when no items are checked", async () => {
    setItems([item({ id: "a", checked: false, foodId: "food-1" })]);

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.addFoodsOnHand).not.toHaveBeenCalled();
    expect(mocks.deleteListItems).not.toHaveBeenCalled();
    expect(mocks.alert.info).not.toHaveBeenCalled();
    expect(mocks.alert.success).not.toHaveBeenCalled();
  });

  test("doesn't panic if the shopping list is null", async () => {
    shoppingList.value = null;

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.addFoodsOnHand).not.toHaveBeenCalled();
  });

  test("keeps the items on the list when the request fails", async () => {
    mocks.addFoodsOnHand.mockResolvedValueOnce({ data: null, error: new Error("nope") });
    setItems([item({ id: "a", checked: true, foodId: "food-1" })]);

    await wrapper.markCheckedItemsOnHand();

    expect(mocks.deleteListItems).not.toHaveBeenCalled();
    expect(mocks.alert.success).not.toHaveBeenCalled();
  });
});
