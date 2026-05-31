import type { IngredientFood, RecipeSummary, ShoppingListItemOut, ShoppingListMultiPurposeLabelOut, ShoppingListOut } from "~/lib/api/types/household";

export const MOCK_ITEM: ShoppingListItemOut = {
  shoppingListId: "",
  id: "",
  groupId: "",
  householdId: "",
  display: "MOCK_ITEM",
  updatedAt: "100",
  position: 1,
  checked: false,
  createdAt: "100",
};

export const MOCK_RECIPE: RecipeSummary = {
  id: "recipe-id",
  name: "Recipe!",
};

export const MOCK_RECIPE2: RecipeSummary = {
  ...MOCK_RECIPE,
  id: undefined,
  name: "Recipe 2!",
};

export const MOCK_FOOD: IngredientFood = {
  id: "1",
  name: "food 1",
};

export const MOCK_FOOD2: IngredientFood = {
  id: "2",
  name: "food 2",
};

export const MOCK_LABEL: ShoppingListMultiPurposeLabelOut = {
  shoppingListId: "",
  labelId: "",
  id: "",
  label: {
    name: "MOCK_LABEL",
    groupId: "",
    id: "",
  },
};

export const MOCK_LABEL2: ShoppingListMultiPurposeLabelOut = {
  shoppingListId: "",
  labelId: "",
  id: "",
  label: {
    name: "MOCK_LABEL2",
    groupId: "",
    id: "",
  },
};

export const MOCK_SHOPPING_LIST: ShoppingListOut = {
  groupId: "",
  userId: "",
  id: "",
  householdId: "",
  labelSettings: [
    MOCK_LABEL,
    MOCK_LABEL2,
  ],
  listItems: [
    MOCK_ITEM,
  ],
  recipeReferences: [{
    id: "",
    shoppingListId: "",
    recipeId: "",
    recipeQuantity: 0,
    recipe: MOCK_RECIPE,
  }, {
    id: "",
    shoppingListId: "",
    recipeId: "",
    recipeQuantity: 0,
    recipe: MOCK_RECIPE2,
  }],
};
