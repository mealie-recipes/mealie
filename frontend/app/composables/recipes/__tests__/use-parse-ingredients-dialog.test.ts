import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { ParsedIngredient, RecipeIngredient } from "~/lib/api/types/recipe";
import { uuid4 } from "../../use-utils";
import { ParseStep, useParseIngredientsDialog } from "../use-parse-ingredients-dialog";
import type { Parser } from "~/lib/api/user/recipes/recipe";

(global as any).uuid4 = uuid4;

const mockError = vi.spyOn((await import("~/composables/use-toast")).alert, "error");

const mockParseIngredients = vi.fn().mockResolvedValue({ data: [{ ingredient: {} }] });
const onSave = vi.fn();
const group = ref({
  aiProviderSettings: { aiEnabled: true },
});
vi.stubGlobal("useGroupSelf", vi.fn().mockReturnValue({ group }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({
    recipes: { parseIngredients: mockParseIngredients },
  }),
}));

vi.mock("../use-recipe-ingredients", () => ({
  useIngredientTextParser: () => ({
    ingredientToParserString: vi.fn().mockReturnValue("4 unit ingredient"),
  }),
}));

const preferences = ref({
  parser: "nlp",
  dontShowInfoPage: true,
});
vi.mock("../../use-users/preferences", () => ({
  useParsingPreferences: () => preferences,
}));

const createFood = vi.fn().mockResolvedValue({ id: "food_id", name: "fuwud" });
const updateFood = vi.fn().mockResolvedValue({ id: "food_id", name: "fuwud" });
const foodStore = {
  actions: {
    createOne: createFood,
    updateOne: updateFood,
  },
};

const createUnit = vi.fn().mockResolvedValue({ id: "unit_id", name: "uwunit" });
const updateUnit = vi.fn().mockResolvedValue({ id: "unit_id", name: "uwunit" });
const unitStore = {
  actions: {
    createOne: createUnit,
    updateOne: updateUnit,
  },
};

vi.mock("~/composables/store", async (importOriginal) => {
  const original: object = await importOriginal();
  return {
    ...original,
    useFoodStore: () => foodStore,
    useUnitStore: () => unitStore,
  };
});

const wrapper = (ingredients: NoUndefinedField<RecipeIngredient>[] = [{}, { referencedRecipe: {} }] as NoUndefinedField<RecipeIngredient>[]) => {
  const TestComponent = defineComponent({
    template: "<div />",
    props: {},
    setup() {
      const x = useParseIngredientsDialog(ingredients, onSave);
      return {
        setCurrentFood(str: string) {
          x.currentMissingFood.value = str;
        },
        setCurrentUnit(str: string) {
          x.currentMissingUnit.value = str;
        },
        setParsedIngs(ings: ParsedIngredient[]) {
          x.parsedIngs.value = ings;
        },
        setShouldDelete(should: boolean) {
          x.currentIngShouldDelete.value = should;
        },
        setCurrentIng(ing: ParsedIngredient) {
          x.currentIng.value = ing;
        },
        setParser(parser: Parser) {
          x.parser.value = parser;
        },
        setDontShow(dontShow: boolean) {
          x.dontShowInfoPage.value = dontShow;
        },
        ...x,
      };
    },
  });

  const wrapper = mount(TestComponent, { props: {} });
  return wrapper;
};

describe("useParseIngredientsDialog", () => {
  beforeEach(() => {
    group.value.aiProviderSettings.aiEnabled = true;
    preferences.value = {
      parser: "nlp",
      dontShowInfoPage: false,
    };
    vi.clearAllMocks();
  });

  describe("nextIngredient", () => {
    test("steps through the ingredients", () => {
      const wrapped = wrapper();
      const { nextIngredient, setParsedIngs } = wrapped.vm;
      setParsedIngs([{
        ingredient: {},
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
      }, {
        ingredient: {
          food: {
            id: "",
            name: "fuwud",
          },
        },
        confidence: { average: 0.99 },
      }, {
        ingredient: {
          unit: {
            id: "",
            name: "uwunit",
          },
        },
        confidence: { average: 0.99 },
      }]);
      const { state } = wrapped.vm;
      expect(state.currentParsedIndex).toBe(-1);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(0);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(1);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(2);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(true);
    });
    test("skips over ingredients that don't need to be reviewed", () => {
      const wrapped = wrapper();
      const { nextIngredient, setParsedIngs } = wrapped.vm;
      setParsedIngs([{
        ingredient: {},
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
        confidence: { average: 0.99 },
      }, {
        ingredient: {
          referencedRecipe: {},
        },
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
        confidence: { average: 0.5 },
      }]);
      const { state } = wrapped.vm;
      expect(wrapped.vm.ingredientsToReviewCount).toBe(2);
      expect(wrapped.vm.autoParsedIngredientsCount).toBe(2);
      expect(state.currentParsedIndex).toBe(-1);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(0);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(true);
    });
    test("skips over deleted ingredients properly", () => {
      const wrapped = wrapper();
      const { nextIngredient, setParsedIngs, setShouldDelete } = wrapped.vm;
      setParsedIngs([{
        ingredient: {},
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
        confidence: { average: 0.5 },
      }]);
      const { state } = wrapped.vm;
      expect(state.currentParsedIndex).toBe(-1);
      expect(state.allReviewed).toBe(false);
      expect(wrapped.vm.currentIngShouldDelete).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(0);
      expect(state.allReviewed).toBe(false);
      expect(wrapped.vm.currentIngShouldDelete).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(1);
      expect(state.allReviewed).toBe(false);
      expect(wrapped.vm.currentIngShouldDelete).toBe(false);
      setShouldDelete(true);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(1);
      expect(state.allReviewed).toBe(false);
      expect(wrapped.vm.currentIngShouldDelete).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(1);
      expect(state.allReviewed).toBe(true);
      expect(wrapped.vm.currentIngShouldDelete).toBe(false);
    });
    test("pulls from cache when it can", async () => {
      const wrapped = wrapper();
      const { createMissingUnit, createMissingFood, nextIngredient, setCurrentUnit, setCurrentFood, setCurrentIng, setParsedIngs } = wrapped.vm;
      setParsedIngs([{
        ingredient: {},
        confidence: { average: 0.5 },
      }, {
        ingredient: {},
      }, {
        ingredient: {
          food: {
            id: "",
            name: "fuwud",
          },
        },
        confidence: { average: 0.99 },
      }, {
        ingredient: {
          unit: {
            id: "",
            name: "uwunit",
          },
        },
        confidence: { average: 0.99 },
      }]);
      setCurrentIng({
        ingredient: {},
      });
      setCurrentUnit("uwunit");
      setCurrentFood("fuwud");
      await createMissingUnit();
      await createMissingFood();
      createUnit.mockClear();
      createFood.mockClear();
      const { state } = wrapped.vm;
      expect(state.currentParsedIndex).toBe(-1);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(0);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(1);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(2);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(false);
      nextIngredient();
      expect(state.currentParsedIndex).toBe(3);
      expect(state.allReviewed).toBe(true);
      expect(createUnit).not.toHaveBeenCalled();
      expect(createFood).not.toHaveBeenCalled();
    });
  });
  describe("nextStep", () => {
    test("walks through the workflow", () => {
      const { nextStep, state } = wrapper().vm;
      expect(state.step).toBe(ParseStep.LOADING);
      nextStep();
      expect(state.step).toBe(ParseStep.INFO);
      nextStep();
      expect(state.step).toBe(ParseStep.PARSE);
      nextStep();
      expect(state.step).toBe(ParseStep.REVIEW);
    });
    test("skips the info page if already seen", () => {
      preferences.value.dontShowInfoPage = true;
      const { nextStep, state } = wrapper().vm;
      expect(state.step).toBe(ParseStep.LOADING);
      nextStep();
      expect(state.step).toBe(ParseStep.PARSE);
      nextStep();
      expect(state.step).toBe(ParseStep.REVIEW);
    });
    test("skips the parse page if nothing to confirm", () => {
      const { nextStep, state } = wrapper().vm;
      state.allReviewed = true;
      expect(state.step).toBe(ParseStep.LOADING);
      nextStep();
      expect(state.step).toBe(ParseStep.INFO);
      nextStep();
      expect(state.step).toBe(ParseStep.REVIEW);
    });
    test("skips the info page if already seen", () => {
      preferences.value.dontShowInfoPage = true;
      const { nextStep, state } = wrapper().vm;
      expect(state.step).toBe(ParseStep.LOADING);
      nextStep();
      expect(state.step).toBe(ParseStep.PARSE);
      nextStep();
      expect(state.step).toBe(ParseStep.REVIEW);
    });
    test("skips the info and parse pages if necessary", () => {
      preferences.value.dontShowInfoPage = true;
      const { nextStep, state } = wrapper().vm;
      state.allReviewed = true;
      expect(state.step).toBe(ParseStep.LOADING);
      nextStep();
      expect(state.step).toBe(ParseStep.REVIEW);
    });
  });
  describe("currentIngHasError", () => {
    test("is true if either food or unit have an error", () => {
      const wrapped = wrapper();
      const { setCurrentFood, setCurrentUnit } = wrapped.vm;
      setCurrentFood("");
      setCurrentUnit("");
      expect(wrapped.vm.currentIngHasError).toBeFalsy();
      setCurrentFood("food");
      setCurrentUnit("");
      expect(wrapped.vm.currentIngHasError).toBeTruthy();
      setCurrentFood("");
      setCurrentUnit("unit");
      expect(wrapped.vm.currentIngHasError).toBeTruthy();
      setCurrentFood("food");
      setCurrentUnit("unit");
      expect(wrapped.vm.currentIngHasError).toBeTruthy();
    });
  });
  describe("availableParsers", () => {
    test("shows open ai parser when available", () => {
      const { availableParsers } = wrapper().vm;
      expect(availableParsers.find(({ value }) => value === "openai")?.hide).toBe(false);
    });
    test("hides open ai parser when not available", () => {
      group.value.aiProviderSettings.aiEnabled = false;
      const { availableParsers } = wrapper().vm;
      expect(availableParsers.find(({ value }) => value === "openai")?.hide).toBe(true);
    });
  });
  test("saveIngs", () => {
    const wrapped = wrapper();
    const { state, saveIngs, setParsedIngs } = wrapped.vm;
    setParsedIngs([{
      ingredient: {},
      confidence: { average: 0.5 },
    }, {
      ingredient: {},
      confidence: { average: 0.99 },
    }, {
      ingredient: {
        referencedRecipe: {},
      },
      confidence: { average: 0.5 },
    }, {
      ingredient: {},
      confidence: { average: 0.5 },
    }]);
    saveIngs();
    expect(state.saveLoading).toBe(true);
    expect(onSave).toHaveBeenCalled();
  });
  describe("parseIngredients", () => {
    test("parses ingredients", async () => {
      const wrapped = wrapper();
      const { state, parseIngredients } = wrapped.vm;
      const promise = parseIngredients();
      expect(state.step).toBe(ParseStep.LOADING);
      expect(state.saveLoading).toBe(false);
      expect(state.loadingCount).toBe(1);
      await promise;
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.loadingCount).toBe(0);
      expect(mockParseIngredients).toHaveBeenCalled();
    });
    test("only makes one call at a time", async () => {
      const wrapped = wrapper();
      const { state, parseIngredients } = wrapped.vm;
      const promise = parseIngredients();
      expect(state.step).toBe(ParseStep.LOADING);
      expect(state.saveLoading).toBe(false);
      expect(state.loadingCount).toBe(1);
      parseIngredients(); // Second call
      await promise;
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.loadingCount).toBe(0);
      expect(mockParseIngredients).toHaveBeenCalledOnce();
    });
    test("doesn't parse from an empty list", async () => {
      const wrapped = wrapper([]);
      const { state, parseIngredients } = wrapped.vm;
      const promise = parseIngredients();
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.saveLoading).toBe(false);
      expect(state.loadingCount).toBe(0);
      await promise;
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.loadingCount).toBe(0);
      expect(mockParseIngredients).not.toHaveBeenCalled();
    });
    test("handles errors gracefully", async () => {
      mockParseIngredients.mockRejectedValue("💥 Woe, exception be upon ye 💥");
      const wrapped = wrapper();
      const { state, parseIngredients } = wrapped.vm;
      const promise = parseIngredients();
      expect(state.step).toBe(ParseStep.LOADING);
      expect(state.saveLoading).toBe(false);
      expect(state.loadingCount).toBe(1);
      await promise;
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.loadingCount).toBe(0);
      expect(mockError).toHaveBeenCalled();
    });
    test("handles errors gracefully", async () => {
      mockParseIngredients.mockResolvedValue({ data: undefined });
      const wrapped = wrapper();
      const { state, parseIngredients } = wrapped.vm;
      const promise = parseIngredients();
      expect(state.step).toBe(ParseStep.LOADING);
      expect(state.saveLoading).toBe(false);
      expect(state.loadingCount).toBe(1);
      await promise;
      expect(state.step).toBe(ParseStep.INFO);
      expect(state.loadingCount).toBe(0);
      expect(mockError).toHaveBeenCalled();
    });
  });
  describe("create and alias food and unit", () => {
    test("createMissingUnit", async () => {
      const wrapped = wrapper();
      const { createMissingUnit, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentUnit("uwunit");
      await createMissingUnit();
      expect(createUnit).toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.unit?.name).toBe("uwunit");
    });
    test("createMissingUnit skips if not missing a unit", async () => {
      const wrapped = wrapper();
      const { createMissingUnit, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentUnit("uwunit");
      await createMissingUnit();
      createUnit.mockClear();
      await createMissingUnit();
      expect(createUnit).not.toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.unit?.name).toBe("uwunit");
    });
    test("createMissingUnit pulls from cache", async () => {
      const wrapped = wrapper();
      const { createMissingUnit, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentUnit("uwunit");
      await createMissingUnit();
      createUnit.mockClear();
      setCurrentUnit("uwunit");
      await createMissingUnit();
      expect(createUnit).not.toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.unit?.name).toBe("uwunit");
    });
    test("createMissingUnit handles undefined values", async () => {
      createUnit.mockReturnValue(undefined);
      const wrapped = wrapper();
      const { createMissingUnit, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentUnit("uwunit");
      await createMissingUnit();
      expect(mockError).toHaveBeenCalled();
    });
    test("createMissingFood", async () => {
      const wrapped = wrapper();
      const { createMissingFood, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentFood("fuwud");
      await createMissingFood();
      expect(createFood).toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.food?.name).toBe("fuwud");
    });
    test("createMissingFood skips if not missing a unit", async () => {
      const wrapped = wrapper();
      const { createMissingFood, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentFood("fuwud");
      await createMissingFood();
      createFood.mockClear();
      await createMissingFood();
      expect(createFood).not.toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.food?.name).toBe("fuwud");
    });
    test("createMissingFood pulls from cache", async () => {
      const wrapped = wrapper();
      const { createMissingFood, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentFood("fuwud");
      await createMissingFood();
      createFood.mockClear();
      setCurrentFood("fuwud");
      await createMissingFood();
      expect(createFood).not.toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.food?.name).toBe("fuwud");
    });
    test("createMissingFood handles undefined values", async () => {
      createFood.mockReturnValue(undefined);
      const wrapped = wrapper();
      const { createMissingFood, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {},
      });
      setCurrentFood("fuwud");
      await createMissingFood();
      expect(mockError).toHaveBeenCalled();
    });
    test("addMissingUnitAsAlias", async () => {
      const wrapped = wrapper();
      const { addMissingUnitAsAlias, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          unit: { name: "2uwunit", id: "unit_id_2" },
        },
      });
      setCurrentUnit("uwunit");
      await addMissingUnitAsAlias();
      expect(updateUnit).toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.unit?.name).toBe("uwunit");
    });
    test("addMissingUnitAsAlias skips if there's no alias to add", async () => {
      const wrapped = wrapper();
      const { addMissingUnitAsAlias, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          unit: { name: "2uwunit", id: "unit_id_2" },
        },
      });
      await addMissingUnitAsAlias();
      expect(updateUnit).not.toHaveBeenCalled();
    });
    test("addMissingUnitAsAlias skips if already includes the alias", async () => {
      const wrapped = wrapper();
      const { addMissingUnitAsAlias, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          unit: { name: "2uwunit", id: "unit_id_2", aliases: [{ name: "uwunit" }] },
        },
      });
      setCurrentUnit("uwunit");
      await addMissingUnitAsAlias();
      expect(updateUnit).not.toHaveBeenCalled();
    });
    test("addMissingUnitAsAlias fails gracefully", async () => {
      updateUnit.mockResolvedValue(undefined);
      const wrapped = wrapper();
      const { addMissingUnitAsAlias, setCurrentUnit, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          unit: { name: "2uwunit", id: "unit_id_2" },
        },
      });
      setCurrentUnit("uwunit");
      await addMissingUnitAsAlias();
      expect(updateUnit).toHaveBeenCalled();
      expect(mockError).toHaveBeenCalled();
    });
    test("addMissingFoodAsAlias", async () => {
      const wrapped = wrapper();
      const { addMissingFoodAsAlias, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          food: { name: "f2uwud", id: "food_id_2" },
        },
      });
      setCurrentFood("fuwud");
      await addMissingFoodAsAlias();
      expect(updateFood).toHaveBeenCalled();
      expect(wrapped.vm.currentIng?.ingredient.food?.name).toBe("fuwud");
    });
    test("addMissingFoodAsAlias skips if there's no alias to add", async () => {
      const wrapped = wrapper();
      const { addMissingFoodAsAlias, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          food: { name: "f2uwud", id: "food_id_2" },
        },
      });
      await addMissingFoodAsAlias();
      expect(updateFood).not.toHaveBeenCalled();
    });
    test("addMissingFoodAsAlias skips if already includes the alias", async () => {
      const wrapped = wrapper();
      const { addMissingFoodAsAlias, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          food: { name: "f2uwud", id: "food_id_2", aliases: [{ name: "fuwud" }] },
        },
      });
      setCurrentFood("fuwud");
      await addMissingFoodAsAlias();
      expect(updateFood).not.toHaveBeenCalled();
    });
    test("addMissingFoodAsAlias fails gracefully", async () => {
      updateFood.mockResolvedValue(undefined);
      const wrapped = wrapper();
      const { addMissingFoodAsAlias, setCurrentFood, setCurrentIng } = wrapped.vm;
      setCurrentIng({
        ingredient: {
          food: { name: "f2uwud", id: "food_id_2" },
        },
      });
      setCurrentFood("fuwud");
      await addMissingFoodAsAlias();
      expect(updateFood).toHaveBeenCalled();
      expect(mockError).toHaveBeenCalled();
    });
  });
  test("parser preferences are stored automatically", async () => {
    preferences.value.parser = "";
    const wrapped = wrapper();
    const { parser, parserPreferences, setParser, setDontShow } = wrapped.vm;
    expect(parser).toBe("nlp");
    expect(parserPreferences.parser).toBe("");
    expect(parserPreferences.dontShowInfoPage).toBe(false);

    setParser("openai");
    setDontShow(true);

    await wrapped.vm.$nextTick();

    const { parserPreferences: newPrefs } = wrapped.vm;
    expect(newPrefs.parser).toBe("openai");
    expect(newPrefs.dontShowInfoPage).toBe(true);
  });
});
