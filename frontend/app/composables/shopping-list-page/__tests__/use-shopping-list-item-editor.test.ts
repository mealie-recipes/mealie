import { beforeEach, describe, expect, test, vi } from "vitest";
import type { ModelRef } from "vue";
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { MOCK_ITEM } from "../sub-composables/__tests__/mocks";
import { useShoppingListItemEditor } from "../use-shopping-list-item-editor";

const foodStore = {
  actions: {
    createOne: vi.fn().mockReturnValue({ id: "food_id" }),
    updateOne: vi.fn(),
  },
};

const unitStore = {
  actions: {
    createOne: vi.fn().mockReturnValue({ id: "unit_id" }),
  },
};

vi.mock("~/composables/store", async (importOriginal) => {
  const actual: object = await importOriginal();
  return {
    ...actual,
    useFoodStore: () => foodStore,
    useUnitStore: () => unitStore,
  };
});

describe("useShoppingListItemEditor", () => {
  const item = ref(MOCK_ITEM) as ModelRef<ShoppingListItemOut>;
  const {
    assignLabelToFood,
    createAssignFood,
    createAssignUnit,
  } = useShoppingListItemEditor(item);

  beforeEach(() => {
    item.value = MOCK_ITEM;
    vi.clearAllMocks();
  });
  describe("createAssignFood", () => {
    test("creates food", () => {
      item.value.food = { id: "food_id", name: "Soylent Green" };
      createAssignFood("Soylent Green");
      expect(foodStore.actions.createOne).toHaveBeenCalled();
    });
    test("creates unit when unit is undefined", () => {
      item.value.food = undefined;
      createAssignFood("Soylent Green");
      expect(foodStore.actions.createOne).toHaveBeenCalled();
    });
    test("does not overwrite unit when something goes wrong", () => {
      foodStore.actions.createOne.mockReturnValueOnce(undefined);
      createAssignFood("Soylent Green");
      expect(item.value.foodId).toBe("food_id");
    });
  });
  describe("createAssignUnit", () => {
    test("creates unit", () => {
      item.value.unit = { id: "unit_id", name: "Wafer" };
      createAssignUnit("Wafer");
      expect(unitStore.actions.createOne).toHaveBeenCalled();
    });
    test("creates unit when unit is undefined", () => {
      item.value.unit = undefined;
      createAssignUnit("Wafer");
      expect(unitStore.actions.createOne).toHaveBeenCalled();
    });
    test("does not overwrite unit when something goes wrong", () => {
      unitStore.actions.createOne.mockReturnValueOnce(undefined);
      createAssignUnit("Wafer");
      expect(item.value.unitId).toBe("unit_id");
    });
  });
  describe("assignLabelToFood", () => {
    beforeEach(() => {
      item.value.food = { id: "food_id", name: "Soylent Green" };
      item.value.foodId = "food_id";
      item.value.labelId = "label_id";
    });
    test("updates food with new label", () => {
      assignLabelToFood();
      expect(foodStore.actions.updateOne).toHaveBeenCalled();
    });
    test("doesn't update when there's no food", () => {
      item.value.food = undefined;
      assignLabelToFood();
      expect(foodStore.actions.updateOne).not.toHaveBeenCalled();
    });
    test("doesn't update when there's no food id", () => {
      item.value.foodId = undefined;
      assignLabelToFood();
      expect(foodStore.actions.updateOne).not.toHaveBeenCalled();
    });
    test("doesn't update when there's no label", () => {
      item.value.labelId = undefined;
      assignLabelToFood();
      expect(foodStore.actions.updateOne).not.toHaveBeenCalled();
    });
  });
});
