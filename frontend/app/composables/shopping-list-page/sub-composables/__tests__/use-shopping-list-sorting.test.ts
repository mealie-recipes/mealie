import { describe, expect, test } from "vitest";
import type { ShoppingListOut } from "~/lib/api/types/household";
import { makeWrapper } from "~/tests/utils";
import { useShoppingListSorting } from "../use-shopping-list-sorting";
import { MOCK_FOOD, MOCK_FOOD2, MOCK_ITEM, MOCK_LABEL, MOCK_LABEL2, MOCK_SHOPPING_LIST } from "./mocks";

const wrapper = () => makeWrapper(() => {
  const { t } = useI18n();
  return {
    t,
    ...useShoppingListSorting(),
  };
});

describe("use-shopping-list-sorting", () => {
  describe("sortItems", () => {
    const { sortItems } = wrapper();
    test("sorts by position first", () => {
      const result = sortItems(MOCK_ITEM, { ...MOCK_ITEM, position: 0 });
      const result2 = sortItems({ ...MOCK_ITEM, position: 0 }, MOCK_ITEM);
      expect(result).toBe(1);
      expect(result2).toBe(-1);
    });
    test("sorts by createdAt next", () => {
      const result = sortItems(MOCK_ITEM, { ...MOCK_ITEM, createdAt: "0" });
      const result2 = sortItems({ ...MOCK_ITEM, createdAt: "0" }, MOCK_ITEM);
      expect(result).toBe(1);
      expect(result2).toBe(-1);
    });
    test("sorts similar items into the same spot", () => {
      const result = sortItems(MOCK_ITEM, MOCK_ITEM);
      expect(result).toBe(0);
    });
    test("handles nulls", () => {
      const result = sortItems(MOCK_ITEM, { ...MOCK_ITEM, position: undefined });
      const result2 = sortItems({ ...MOCK_ITEM, position: undefined }, MOCK_ITEM);
      expect(result).toBe(1);
      expect(result2).toBe(-1);
    });
    test("handles nulls", () => {
      const result = sortItems(MOCK_ITEM, { ...MOCK_ITEM, createdAt: undefined });
      const result2 = sortItems({ ...MOCK_ITEM, createdAt: undefined }, MOCK_ITEM);
      expect(result).toBe(1);
      expect(result2).toBe(-1);
    });
  });
  describe("sortListItems", () => {
    const { sortListItems } = wrapper();
    test("sorts by position first", () => {
      const sortedList = { ...MOCK_SHOPPING_LIST, listItems: [MOCK_ITEM, { ...MOCK_ITEM, position: 0 }, { ...MOCK_ITEM, createdAt: "0" }] };
      sortListItems(sortedList);
      expect(sortedList.listItems).toEqual([
        { ...MOCK_ITEM, position: 0 },
        { ...MOCK_ITEM, createdAt: "0" },
        MOCK_ITEM,
      ]);
    });
    test("handles nulls", () => {
      const sortedList = { ...MOCK_SHOPPING_LIST, listItems: undefined };
      sortListItems(sortedList);
      expect(sortedList.listItems).toEqual(undefined);
    });
  });
  describe("updateItemsByLabel", () => {
    const { updateItemsByLabel, t } = wrapper();
    test("sorts by group", () => {
      const sortedList = {
        ...MOCK_SHOPPING_LIST, listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
        ],
      };
      const result = updateItemsByLabel(sortedList);
      expect(result).toEqual({
        [t("shopping-list.no-label")]: [
          MOCK_ITEM,
        ],
        [MOCK_LABEL.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
        ],
        [MOCK_LABEL2.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
        ],
      });
    });
    test("ignores checked items", () => {
      const sortedList = {
        ...MOCK_SHOPPING_LIST, listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1", checked: true },
        ],
      };
      const result = updateItemsByLabel(sortedList);
      expect(result).toEqual({
        [t("shopping-list.no-label")]: [
          MOCK_ITEM,
        ],
        [MOCK_LABEL.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
        ],
        [MOCK_LABEL2.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
        ],
      });
    });
    test("returns unordered labels if no ordering is specified", () => {
      const sortedList = {
        ...MOCK_SHOPPING_LIST,
        labelSettings: undefined,
        listItems: [
          MOCK_ITEM,
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1", checked: true },
        ],
      };
      const result = updateItemsByLabel(sortedList);
      expect(result).toEqual({
        [t("shopping-list.no-label")]: [
          MOCK_ITEM,
        ],
        [MOCK_LABEL2.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL2.label, labelId: "2" },
        ],
        [MOCK_LABEL.label.name]: [
          { ...MOCK_ITEM, label: MOCK_LABEL.label, labelId: "1" },
        ],
      });
    });
  });
  describe("groupAndSortListItemsByFood", () => {
    const { groupAndSortListItemsByFood } = wrapper();
    test("sorts by group", () => {
      const sortedList = { ...MOCK_SHOPPING_LIST };
      groupAndSortListItemsByFood(sortedList);
      expect(sortedList.listItems).toEqual(MOCK_SHOPPING_LIST.listItems);
    });
    test("groups checked items together", () => {
      const sortedList: ShoppingListOut = {
        ...MOCK_SHOPPING_LIST, listItems: [
          { ...MOCK_ITEM, checked: true, food: MOCK_FOOD },
          { ...MOCK_ITEM, checked: true, food: MOCK_FOOD2 },
        ],
      };
      groupAndSortListItemsByFood(sortedList);
      expect(sortedList.listItems).toEqual([
        { ...MOCK_ITEM, checked: true, food: MOCK_FOOD },
        { ...MOCK_ITEM, checked: true, food: MOCK_FOOD2, position: 1 },
      ]);
    });
    test("populates position and created at if not present", () => {
      const sortedList: ShoppingListOut = {
        ...MOCK_SHOPPING_LIST, listItems: [
          { ...MOCK_ITEM, food: MOCK_FOOD, position: undefined },
          { ...MOCK_ITEM, food: MOCK_FOOD2, createdAt: undefined },
        ],
      };
      groupAndSortListItemsByFood(sortedList);
      expect(sortedList.listItems).toEqual([
        { ...MOCK_ITEM, food: MOCK_FOOD2, createdAt: undefined },
        { ...MOCK_ITEM, food: MOCK_FOOD, position: 1 },
      ]);
    });
    test("handles nulls", () => {
      const sortedList: ShoppingListOut = { ...MOCK_SHOPPING_LIST, listItems: undefined };
      groupAndSortListItemsByFood(sortedList);
      expect(sortedList.listItems).toEqual(undefined);
    });
  });
});
