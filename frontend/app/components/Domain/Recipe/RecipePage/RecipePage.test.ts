import { flushPromises, mount, type VueWrapper } from "@vue/test-utils";
import { nextTick, reactive, ref } from "vue";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import RecipePage from "./RecipePage.vue";
import { clearPageState } from "~/composables/recipe-page/shared-state";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeIngredient } from "~/lib/api/types/recipe";

const mocks = vi.hoisted(() => ({ updateOne: vi.fn() }));

vi.mock("../RecipeIngredients.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageEditorToolbar.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageFooter.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageHeader.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageIngredientEditor.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageIngredientToolsView.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageInstructions.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageOrganizers.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipeParseDialog/RecipePageParseDialog.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageScale.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageInfoEditor.vue", () => ({ default: { render: () => null } }));
vi.mock("./RecipePageParts/RecipePageComments.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/Recipe/RecipePrintContainer.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/Recipe/RecipeDialogBulkAdd.vue", () => ({ default: { render: () => null } }));
vi.mock("~/components/Domain/Recipe/RecipeNotes.vue", () => ({ default: { render: () => null } }));

vi.mock("~/composables/api", () => ({
  useUserApi: () => ({ recipes: { updateOne: mocks.updateOne } }),
}));
vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({ isOwnGroup: ref(true) }),
}));
vi.mock("~/composables/use-navigation-warning", () => ({
  useNavigationWarning: () => ({ activateNavigationWarning: vi.fn(), deactivateNavigationWarning: vi.fn() }),
}));
vi.mock("~/composables/recipes", () => ({
  useUnitSystem: () => ({ unitSystem: ref(null) }),
  useUnitConversion: () => ({ convertIngredient: vi.fn() }),
}));
vi.mock("~/composables/use-households", () => ({
  useHouseholdSelf: () => ({ household: ref(null) }),
}));

interface RecipePageInstance {
  recipe: NoUndefinedField<Recipe>;
  instructionForm: { validate: () => Promise<{ valid: boolean }> };
  toggleIsParsing: (value: boolean) => void;
  saveParsedIngredients: (ingredients: NoUndefinedField<RecipeIngredient[]>) => Promise<void>;
  saveRecipe: () => Promise<void>;
}

describe("RecipePage parsing navigation", () => {
  let wrapper: VueWrapper | undefined;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("useDisplay", () => ({ smAndUp: ref(true) }));
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "home" }) }));
    vi.stubGlobal("onBeforeRouteLeave", vi.fn());
  });

  afterEach(() => {
    wrapper?.unmount();
    wrapper = undefined;
    clearPageState("original");
    clearPageState("renamed");
    vi.unstubAllGlobals();
  });

  async function mountPage(query: Record<string, string | undefined> = { edit: "true" }) {
    const route = reactive({
      params: { groupSlug: "home", slug: "original" },
      query,
    });
    const replace = vi.fn((target: string | { query: Record<string, string | undefined> }) => {
      if (typeof target === "string") {
        route.params.slug = target.split("/").at(-1)!;
        route.query = {};
      }
      else {
        route.query = target.query;
      }
      return Promise.resolve();
    });
    vi.stubGlobal("useRoute", () => route);
    vi.stubGlobal("useRouter", () => ({ replace }));

    const recipe = {
      id: "recipe-1",
      slug: "original",
      name: "Original",
      recipeIngredient: [],
      recipeInstructions: [],
    } as unknown as NoUndefinedField<Recipe>;
    // Exercise the page's save handlers and route watchers without rendering its editors.
    wrapper = mount({ ...RecipePage, render: () => null }, {
      props: { modelValue: recipe },
    });
    await flushPromises();
    const page = wrapper.vm as unknown as RecipePageInstance;
    page.instructionForm = { validate: async () => ({ valid: true }) };
    return { page, route, replace };
  }

  test("keeps the renamed route after saving parsed ingredients and uses it for the next save", async () => {
    const { page, route, replace } = await mountPage();
    page.recipe.name = "Renamed";
    page.toggleIsParsing(true);
    await nextTick();
    const ingredients = [{ note: "2 cups flour" }] as NoUndefinedField<RecipeIngredient[]>;
    const savedRecipe = { ...page.recipe, slug: "renamed", recipeIngredient: ingredients };
    mocks.updateOne.mockResolvedValue({ data: savedRecipe, error: null });

    await page.saveParsedIngredients(ingredients);
    await flushPromises();

    expect(mocks.updateOne).toHaveBeenCalledWith("original", expect.objectContaining({ name: "Renamed", recipeIngredient: ingredients }));
    expect(replace).toHaveBeenCalledExactlyOnceWith("/g/home/r/renamed");
    expect(route.params.slug).toBe("renamed");

    await page.saveRecipe();
    await flushPromises();
    expect(mocks.updateOne).toHaveBeenLastCalledWith("renamed", expect.anything());
  });

  test("still removes an existing parse query when the dialog closes", async () => {
    const { page, route, replace } = await mountPage({ edit: "true", parse: "true" });

    page.toggleIsParsing(false);
    await flushPromises();

    expect(replace).toHaveBeenCalledOnce();
    expect(route.query).toEqual({ edit: "true", parse: undefined });
  });
});
