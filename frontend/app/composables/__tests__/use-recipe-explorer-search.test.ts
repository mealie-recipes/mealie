import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { computed, effectScope, nextTick, reactive, ref } from "vue";
import { clearRecipeExplorerSearchState, useRecipeExplorerSearch } from "../use-recipe-explorer-search";

vi.mock("~/composables/store", () => {
  const store = () => ({ store: ref([]) });
  return Object.fromEntries(["Category", "Food", "Household", "Tag", "Tool"].flatMap(name => [
    [`use${name}Store`, store], [`usePublic${name}Store`, store],
  ]));
});
const context = vi.hoisted(() => ({ own: true }));
vi.mock("~/composables/use-logged-in-state", () => ({ useLoggedInState: () => ({ isOwnGroup: { value: context.own } }) }));
vi.mock("~/composables/use-users/preferences", () => ({
  useUserSearchQuerySession: () => ref({ recipe: "" }),
  useUserSortPreferences: () => ref({ orderBy: "created_at", orderDirection: "desc" }),
}));
vi.mock("vue-i18n", async original => ({
  ...await original<typeof import("vue-i18n")>(),
  useI18n: () => ({ t: (key: string) => key }),
}));

let scope: ReturnType<typeof effectScope>;
let route: { query: Record<string, unknown> };
let search: ReturnType<typeof useRecipeExplorerSearch>;
let push: ReturnType<typeof vi.fn>;

beforeEach(() => {
  context.own = true;
  route = reactive({ query: {} });
  push = vi.fn(async ({ query }) => { route.query = query; await nextTick(); });
  vi.stubGlobal("useMealieAuth", () => ({ user: ref({ id: "me", groupSlug: "home" }) }));
  vi.stubGlobal("useRoute", () => route);
  vi.stubGlobal("useRouter", () => ({ currentRoute: ref(route), push, replace: push }));
  scope = effectScope();
});
afterEach(() => {
  scope.stop();
  clearRecipeExplorerSearchState("home");
  vi.unstubAllGlobals();
});

function create() {
  search = scope.run(() => useRecipeExplorerSearch(computed(() => "home")))!;
  return search;
}

const flushHistory = async () => {
  await nextTick();
  await nextTick();
  await nextTick();
};

describe("recipe explorer search", () => {
  test("applies favorites and clears filters without losing the search text", async () => {
    create();
    await search.initialize();
    search.state.value.search = "pork";
    search.state.value.favoritesOnly = true;
    expect(search.passedQueryWithSeed.value.search).toBe("");
    await search.search();
    expect(search.passedQueryWithSeed.value.search).toBe("pork");
    expect(search.passedQueryWithSeed.value.queryFilter).toBe("favoritedBy.id = \"me\"");
    expect(route.query.favoritesOnly).toBe("true");
    search.clearFilters();
    expect(search.state.value.search).toBe("pork");
    await search.search();
    expect(search.passedQueryWithSeed.value.queryFilter).toBe("");
  });

  test("restores URL sorting and filters on history navigation", async () => {
    route.query = { search: "lettuce", orderBy: "rating", orderDirection: "asc", favoritesOnly: "true", auto: "false" };
    create();
    await search.initialize();
    expect(search.state.value.orderBy).toBe("rating");
    expect(search.state.value.orderDirection).toBe("asc");
    expect(search.state.value.favoritesOnly).toBe(true);
    expect(search.state.value.auto).toBe(false);
    route.query = { search: "pork", orderBy: "name", orderDirection: "desc" };
    await flushHistory();
    expect(search.passedQueryWithSeed.value.search).toBe("pork");
    expect(search.state.value.favoritesOnly).toBe(false);
    expect(search.state.value.auto).toBe(true);
    expect(search.passedQueryWithSeed.value.orderBy).toBe("name");
  });

  test("honors manual search and resets the search and filters", async () => {
    vi.useFakeTimers();
    try {
      route.query = { auto: "false" };
      create();
      await search.initialize();
      push.mockClear();
      search.state.value.search = "pork";
      search.state.value.favoritesOnly = true;
      await nextTick();
      await vi.advanceTimersByTimeAsync(600);
      expect(push).not.toHaveBeenCalled();
      await search.search();
      expect(search.passedQueryWithSeed.value.search).toBe("pork");
      expect(route.query.auto).toBe("false");
      search.reset();
      expect(search.state.value.search).toBe("");
      expect(search.state.value.favoritesOnly).toBe(false);
      expect(search.state.value.orderBy).toBe("created_at");
      expect(search.state.value.orderDirection).toBe("desc");
      expect(search.state.value.auto).toBe(false);
    }
    finally {
      vi.useRealTimers();
    }
  });

  test("ignores old advanced filter URLs", async () => {
    route.query = { advancedFilter: "invalid JSON" };
    create();
    await search.initialize();
    expect(search.passedQueryWithSeed.value.queryFilter).toBe("");
  });

  test("ignores private filters and last-made sort on public groups", async () => {
    context.own = false;
    route.query = { favoritesOnly: "true", advancedFilter: "invalid JSON", orderBy: "last_made" };
    create();
    await search.initialize();
    expect(search.state.value.favoritesOnly).toBe(false);
    expect(search.passedQueryWithSeed.value.queryFilter).toBeUndefined();
    expect(search.passedQueryWithSeed.value.orderBy).toBe("created_at");
  });
});
