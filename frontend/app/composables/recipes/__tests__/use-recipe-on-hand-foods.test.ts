import { beforeEach, describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import { useRecipeOnHandFoods } from "../use-recipe-on-hand-foods";
import type { Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

const mocks = vi.hoisted(() => ({
  removeFoodsOnHand: vi.fn(),
}));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    households: { removeFoodsOnHand: mocks.removeFoodsOnHand },
  }),
}));

const HOUSEHOLD = "my-household";

function ingredient(id: string, name: string, households: string[]): RecipeIngredient {
  return { food: { id, name, householdsWithIngredientFood: households } };
}

function recipeWith(recipeIngredient: RecipeIngredient[]): Recipe {
  return { id: "recipe-id", recipeIngredient };
}

describe("useRecipeOnHandFoods", () => {
  const recipe = ref<Recipe>(recipeWith([]));
  const householdSlug = ref<string | undefined>(HOUSEHOLD);

  beforeEach(() => {
    vi.clearAllMocks();
    mocks.removeFoodsOnHand.mockResolvedValue({ data: { message: "", error: false }, error: null });
    householdSlug.value = HOUSEHOLD;
    recipe.value = recipeWith([
      ingredient("flour", "flour", [HOUSEHOLD]),
      ingredient("flour", "flour", [HOUSEHOLD]),
      ingredient("milk", "milk", ["other-household", HOUSEHOLD]),
      ingredient("eggs", "eggs", ["other-household"]),
      { note: "a pinch of something" },
    ]);
  });

  test("lists each food the household has on hand once", () => {
    const { onHandFoods } = useRecipeOnHandFoods(recipe, householdSlug);

    expect(onHandFoods.value).toEqual([
      { id: "flour", name: "flour" },
      { id: "milk", name: "milk" },
    ]);
  });

  test("lists nothing without a household", () => {
    householdSlug.value = undefined;
    const { onHandFoods } = useRecipeOnHandFoods(recipe, householdSlug);

    expect(onHandFoods.value).toEqual([]);
  });

  test("removes the used-up foods and stops listing them", async () => {
    const { onHandFoods, usedUpFoodIds, removeUsedUpFoods } = useRecipeOnHandFoods(recipe, householdSlug);
    usedUpFoodIds.value = ["flour"];

    expect(await removeUsedUpFoods()).toBe(true);

    expect(mocks.removeFoodsOnHand).toHaveBeenCalledExactlyOnceWith(["flour"]);
    expect(usedUpFoodIds.value).toEqual([]);
    expect(onHandFoods.value).toEqual([{ id: "milk", name: "milk" }]);
  });

  test("doesn't call the API when nothing is used up", async () => {
    const { removeUsedUpFoods } = useRecipeOnHandFoods(recipe, householdSlug);

    expect(await removeUsedUpFoods()).toBe(true);
    expect(mocks.removeFoodsOnHand).not.toHaveBeenCalled();
  });

  test("keeps the foods listed when the request fails", async () => {
    mocks.removeFoodsOnHand.mockResolvedValueOnce({ data: null, error: new Error("nope") });
    const { onHandFoods, usedUpFoodIds, removeUsedUpFoods } = useRecipeOnHandFoods(recipe, householdSlug);
    usedUpFoodIds.value = ["milk"];

    expect(await removeUsedUpFoods()).toBe(false);

    expect(usedUpFoodIds.value).toEqual(["milk"]);
    expect(onHandFoods.value).toHaveLength(2);
  });

  test("resets the picked foods", () => {
    const { usedUpFoodIds, resetUsedUpFoods } = useRecipeOnHandFoods(recipe, householdSlug);
    usedUpFoodIds.value = ["flour", "milk"];

    resetUsedUpFoods();

    expect(usedUpFoodIds.value).toEqual([]);
  });
});
