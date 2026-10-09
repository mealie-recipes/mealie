import { describe, expect, test } from "vitest";
import type { ShoppingListOut } from "~/lib/api/types/household";
import { makeWrapper } from "~/tests/utils";
import { useShoppingListLabels } from "../use-shopping-list-labels";
import { MOCK_ITEM, MOCK_LABEL, MOCK_LABEL2, MOCK_LABEL3, MOCK_SHOPPING_LIST } from "./mocks";

const wrapper = (list: ShoppingListOut = MOCK_SHOPPING_LIST) => makeWrapper(() => {
  const shoppingList = ref(list);
  const state = useShoppingListLabels(shoppingList);
  const { t } = useI18n();
  return {
    shoppingList,
    t,
    ...state,
  };
});

describe("use-shopping-list-labels", () => {
  describe("getLabelColor", () => {
    const { getLabelColor, t } = wrapper({
      ...MOCK_SHOPPING_LIST,
      listItems: [
        { ...MOCK_ITEM, label: MOCK_LABEL.label },
        { ...MOCK_ITEM, label: MOCK_LABEL2.label },
        { ...MOCK_ITEM, label: MOCK_LABEL3.label },
      ],
    });

    test("gets the correct color", () => {
      const color1 = getLabelColor(MOCK_LABEL.label.name);
      const color2 = getLabelColor(MOCK_LABEL2.label.name);
      expect(color1).toBe(MOCK_LABEL.label.color);
      expect(color2).toBe(MOCK_LABEL2.label.color);
    });
    test("handles undefined names", () => {
      const color1 = getLabelColor(t("shopping-list.no-label"));
      expect(color1).toBe(MOCK_LABEL3.label.color);
    });
    test("handles undefined items", () => {
      const { getLabelColor } = wrapper({
        ...MOCK_SHOPPING_LIST,
        listItems: undefined,
      });
      const color1 = getLabelColor(MOCK_LABEL.label.name);
      expect(color1).toBe(undefined);
    });
  });
});
