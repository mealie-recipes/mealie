import type { IngredientFoodOut, RecipeSummary, ShoppingListItemOut, ShoppingListMultiPurposeLabelOut, ShoppingListOut } from "~/lib/api/types/household";
import {
  makeIngredientFood,
  makeLabel,
  makeRecipeSummary,
  makeShoppingList,
  makeShoppingListItem,
  makeShoppingListLabelSetting,
} from "~/tests/factories";

export const MOCK_ITEM: ShoppingListItemOut = makeShoppingListItem({
  shoppingListId: "",
  id: "",
  groupId: "",
  householdId: "",
  display: "MOCK_ITEM",
  updatedAt: "100",
  position: 1,
  checked: false,
  createdAt: "100",
});

export const MOCK_RECIPE: RecipeSummary = makeRecipeSummary({
  id: "recipe-id",
  name: "Recipe!",
});

export const MOCK_RECIPE2: RecipeSummary = {
  ...MOCK_RECIPE,
  id: "recipe-id-2",
  name: "Recipe 2!",
};

export const MOCK_FOOD: IngredientFoodOut = makeIngredientFood({
  id: "1",
  name: "food 1",
});

export const MOCK_FOOD2: IngredientFoodOut = makeIngredientFood({
  id: "2",
  name: "food 2",
});

export const MOCK_LABEL: ShoppingListMultiPurposeLabelOut = makeShoppingListLabelSetting({
  shoppingListId: "",
  labelId: "",
  id: "",
  label: makeLabel({ name: "MOCK_LABEL", groupId: "", id: "", color: "color1" }),
});

export const MOCK_LABEL2: ShoppingListMultiPurposeLabelOut = makeShoppingListLabelSetting({
  shoppingListId: "",
  labelId: "",
  id: "",
  label: makeLabel({ name: "MOCK_LABEL2", groupId: "", id: "", color: "color2" }),
});

export const MOCK_LABEL3: ShoppingListMultiPurposeLabelOut = makeShoppingListLabelSetting({
  shoppingListId: "",
  labelId: "",
  id: "",
  label: makeLabel({ name: "", groupId: "", id: "", color: "" }),
});

export const MOCK_SHOPPING_LIST: ShoppingListOut = makeShoppingList({
  groupId: "",
  userId: "",
  id: "",
  householdId: "",
  name: null,
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
});
