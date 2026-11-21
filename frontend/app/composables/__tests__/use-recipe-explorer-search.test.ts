import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { computed, effectScope, nextTick, reactive, ref } from "vue";
import { clearRecipeExplorerSearchState, useRecipeExplorerSearch } from "../use-recipe-explorer-search";

vi.mock("~/composables/store", () => {
  const store = () => ({ store: ref([]) });
  return Object.fromEntries([
    "useCategoryStore", "usePublicCategoryStore", "useFoodStore", "usePublicFoodStore",
    "useHouseholdStore", "usePublicHouseholdStore", "useTagStore", "usePublicTagStore",
    "useToolStore", "usePublicToolStore",
  ].map(name => [name, store]));
});
vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({ isOwnGroup: ref(true) }),
}));
vi.mock("~/composables/use-users/preferences", () => ({
  useUserSearchQuerySession: () => ref({ recipe: "" }),
  useUserSortPreferences: () => ref({ orderBy: "name", orderDirection: "asc" }),
}));

let scope: ReturnType<typeof effectScope>;
let route: { query: Record<string, unknown> };
let push: ReturnType<typeof vi.fn>;

beforeEach(() => {
  scope = effectScope();
  route = reactive({ query: { search: "+pork -\"chili peppers\"", searchMode: "any" } });
  push = vi.fn(async ({ query }) => { route.query = query; });
  vi.stubGlobal("useRouter", () => ({ currentRoute: ref(route), push, replace: push }));
  vi.stubGlobal("useRoute", () => route);
});

afterEach(() => {
  scope.stop();
  clearRecipeExplorerSearchState("home");
  vi.unstubAllGlobals();
});

describe("recipe explorer search modes", () => {
  test("restores query syntax and mode from the URL", async () => {
    const search = scope.run(() => useRecipeExplorerSearch(computed(() => "home")))!;
    await search.initialize();
    expect(search.state.value.search).toBe("+pork -\"chili peppers\"");
    expect(search.state.value.searchMode).toBe("any");
    expect(search.passedQueryWithSeed.value.searchMode).toBe("any");
  });

  test("resets mode for new text and persists explicit broader searches", async () => {
    const search = scope.run(() => useRecipeExplorerSearch(computed(() => "home")))!;
    await search.initialize();
    search.state.value.search = "lettuce cups";
    expect(search.state.value.searchMode).toBe("all");
    await search.search();
    expect(push).toHaveBeenLastCalledWith(expect.objectContaining({
      query: expect.objectContaining({ search: "lettuce cups", searchMode: undefined }),
    }));
    search.state.value.searchMode = "any";
    await search.search();
    expect(route.query.searchMode).toBe("any");
  });

  test("restores mode and text on browser history changes", async () => {
    const search = scope.run(() => useRecipeExplorerSearch(computed(() => "home")))!;
    await search.initialize();
    route.query = { search: "+chicken", searchMode: "any" };
    await nextTick();
    await nextTick();
    expect(search.state.value.search).toBe("+chicken");
    expect(search.state.value.searchMode).toBe("any");
    expect(search.passedQueryWithSeed.value.search).toBe("+chicken");
  });
});
