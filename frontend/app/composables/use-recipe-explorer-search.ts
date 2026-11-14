import { recipeSortOptions } from "~/composables/use-recipe-search-options";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { watchDebounced } from "@vueuse/shared";
import type { IngredientFoodOut, CategoryOut, TagOut, ToolOut } from "~/lib/api/types/recipe";
import type { HouseholdSummary } from "~/lib/api/types/household";
import type { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";
import {
  useCategoryStore,
  usePublicCategoryStore,
  useFoodStore,
  usePublicFoodStore,
  useHouseholdStore,
  usePublicHouseholdStore,
  useTagStore,
  usePublicTagStore,
  useToolStore,
  usePublicToolStore,
} from "~/composables/store";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useUserSearchQuerySession, useUserSortPreferences } from "~/composables/use-users/preferences";

// Type for the composable return value
interface RecipeExplorerSearchState {
  state: Ref<{
    favoritesOnly: boolean;
    auto: boolean;
    ready: boolean;
    search: string;
    orderBy: string;
    orderDirection: "asc" | "desc";
    requireAllCategories: boolean;
    requireAllTags: boolean;
    requireAllTools: boolean;
    requireAllFoods: boolean;
    randomSeed: number;
  }>;
  selectedCategories: Ref<CategoryOut[]>;
  selectedFoods: Ref<IngredientFoodOut[]>;
  selectedHouseholds: Ref<NoUndefinedField<HouseholdSummary>[]>;
  selectedTags: Ref<TagOut[]>;
  selectedTools: Ref<ToolOut[]>;
  passedQueryWithSeed: ComputedRef<RecipeSearchQuery & { _searchSeed: string }>;
  search: () => Promise<void>;
  reset: () => void;
  clearFilters: () => void;
  toggleOrderDirection: () => void;
  setOrderBy: (value: string) => void;
  setRandomOrderBy: () => void;
  filterItems: (item: CategoryOut | TagOut | ToolOut, urlPrefix: string) => void;
  initialize: () => Promise<void>;
}

// Memo storage for singleton instances
const memo: Record<string, RecipeExplorerSearchState> = {};

function createRecipeExplorerSearchState(groupSlug: ComputedRef<string>): RecipeExplorerSearchState {
  const auth = useMealieAuth();
  let hydrating = false;
  let updatingRoute = false;
  const router = useRouter();
  const route = useRoute();

  const { isOwnGroup } = useLoggedInState();
  const searchQuerySession = useUserSearchQuerySession();
  const sortPreferences = useUserSortPreferences();

  // State management
  const state = ref({
    favoritesOnly: false,
    auto: true,
    ready: false,
    search: "",
    orderBy: "created_at",
    orderDirection: "desc" as "asc" | "desc",
    requireAllCategories: false,
    requireAllTags: false,
    requireAllTools: false,
    requireAllFoods: false,
    randomSeed: 0,
  });

  // Store references
  const categories = isOwnGroup.value ? useCategoryStore() : usePublicCategoryStore(groupSlug.value);
  const foods = isOwnGroup.value ? useFoodStore() : usePublicFoodStore(groupSlug.value);
  const households = isOwnGroup.value ? useHouseholdStore() : usePublicHouseholdStore(groupSlug.value);
  const tags = isOwnGroup.value ? useTagStore() : usePublicTagStore(groupSlug.value);
  const tools = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);

  // Selected items
  const selectedCategories = ref<CategoryOut[]>([]);
  const selectedFoods = ref<IngredientFoodOut[]>([]);
  const selectedHouseholds = ref<NoUndefinedField<HouseholdSummary>[]>([]);
  const selectedTags = ref<TagOut[]>([]);
  const selectedTools = ref<ToolOut[]>([]);

  // Query defaults
  const queryDefaults = {
    search: "",
    orderBy: "created_at",
    orderDirection: "desc" as "asc" | "desc",
    requireAllCategories: false,
    requireAllTags: false,
    requireAllTools: false,
    requireAllFoods: false,
  };

  // Sync sort preferences
  watch(() => state.value.orderBy, (newValue) => {
    sortPreferences.value.orderBy = newValue;
  });

  watch(() => state.value.orderDirection, (newValue) => {
    sortPreferences.value.orderDirection = newValue;
  });

  // Utility functions
  function toIDArray(array: { id: string }[]) {
    return array.map(item => item.id).sort();
  }

  function calcPassedQuery(): RecipeSearchQuery {
    const orderBy = !isOwnGroup.value && state.value.orderBy === "last_made"
      ? queryDefaults.orderBy
      : state.value.orderBy;

    return {
      queryFilter: isOwnGroup.value ? (state.value.favoritesOnly && auth.user.value?.id ? `favoritedBy.id = "${auth.user.value.id}"` : "") : undefined,
      search: state.value.search ? state.value.search : "",
      categories: toIDArray(selectedCategories.value),
      foods: toIDArray(selectedFoods.value),
      households: toIDArray(selectedHouseholds.value),
      tags: toIDArray(selectedTags.value),
      tools: toIDArray(selectedTools.value),
      requireAllCategories: state.value.requireAllCategories,
      requireAllTags: state.value.requireAllTags,
      requireAllTools: state.value.requireAllTools,
      requireAllFoods: state.value.requireAllFoods,
      orderBy,
      orderDirection: state.value.orderDirection,
    };
  }

  const passedQuery = ref<RecipeSearchQuery>(calcPassedQuery());

  const passedQueryWithSeed = computed(() => {
    return {
      ...passedQuery.value,
      _searchSeed: Date.now().toString(),
      _randomSeed: state.value.randomSeed,
    };
  });

  // Update the seed to trigger a new search
  function setRandomOrderBy() {
    state.value.orderBy = "random";
    state.value.randomSeed = Date.now();
  }

  // Wait utility for async hydration
  function waitUntilAndExecute(
    condition: () => boolean,
    callback: () => void,
    opts = { timeout: 2000, interval: 500 },
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const state = {
        timeout: undefined as number | undefined,
        interval: undefined as number | undefined,
      };

      const check = () => {
        if (condition()) {
          clearInterval(state.interval);
          clearTimeout(state.timeout);
          callback();
          resolve();
        }
      };

      state.interval = setInterval(check, opts.interval) as unknown as number;
      state.timeout = setTimeout(() => {
        clearInterval(state.interval);
        reject(new Error("Timeout"));
      }, opts.timeout) as unknown as number;
    });
  }

  // Main functions
  function clearFilters() {
    state.value.favoritesOnly = false;
    state.value.requireAllCategories = false;
    state.value.requireAllTags = false;
    state.value.requireAllTools = false;
    state.value.requireAllFoods = false;
    selectedCategories.value = [];
    selectedFoods.value = [];
    selectedHouseholds.value = [];
    selectedTags.value = [];
    selectedTools.value = [];
  }

  function reset() {
    clearFilters();
    state.value.search = queryDefaults.search;
    state.value.orderBy = queryDefaults.orderBy;
    state.value.orderDirection = queryDefaults.orderDirection;
    sortPreferences.value.orderBy = queryDefaults.orderBy;
    sortPreferences.value.orderDirection = queryDefaults.orderDirection;
  }

  function toggleOrderDirection() {
    state.value.orderDirection = state.value.orderDirection === "asc" ? "desc" : "asc";
    sortPreferences.value.orderDirection = state.value.orderDirection;
  }

  function setOrderBy(value: string) {
    if (!isOwnGroup.value && value === "last_made") {
      value = queryDefaults.orderBy;
    }

    state.value.orderBy = value;
    sortPreferences.value.orderBy = value;
  }

  async function search() {
    const oldQueryValueString = JSON.stringify(passedQuery.value);
    const newQueryValue = calcPassedQuery();
    const newQueryValueString = JSON.stringify(newQueryValue);
    if (oldQueryValueString === newQueryValueString && state.value.orderBy !== "random") {
      return;
    }

    passedQuery.value = newQueryValue;
    const query = {
      favoritesOnly: isOwnGroup.value && state.value.favoritesOnly ? "true" : undefined,
      orderBy: state.value.orderBy,
      orderDirection: state.value.orderDirection,
      categories: passedQuery.value.categories,
      foods: passedQuery.value.foods,
      tags: passedQuery.value.tags,
      tools: passedQuery.value.tools,
      // Only add the query param if it's not the default value
      ...{
        auto: state.value.auto ? undefined : "false",
        search: passedQuery.value.search === queryDefaults.search ? undefined : passedQuery.value.search,
        households: !passedQuery.value.households?.length || passedQuery.value.households?.length === households.store.value.length ? undefined : passedQuery.value.households,
        requireAllCategories: passedQuery.value.requireAllCategories ? "true" : undefined,
        requireAllTags: passedQuery.value.requireAllTags ? "true" : undefined,
        requireAllTools: passedQuery.value.requireAllTools ? "true" : undefined,
        requireAllFoods: passedQuery.value.requireAllFoods ? "true" : undefined,
      },
    };
    updatingRoute = true;
    try {
      await router.push({ query });
    }
    finally {
      updatingRoute = false;
    }
    searchQuerySession.value.recipe = JSON.stringify(query);
  }

  function filterItems(item: CategoryOut | TagOut | ToolOut, urlPrefix: string) {
    if (urlPrefix === "categories") {
      const result = categories.store.value.filter(category => category.id.includes(item.id));
      selectedCategories.value = result;
    }
    else if (urlPrefix === "tags") {
      const result = tags.store.value.filter(tag => tag.id.includes(item.id));
      selectedTags.value = result;
    }
    else if (urlPrefix === "tools") {
      const result = tools.store.value.filter(tool => tool.id.includes(item.id));
      selectedTools.value = result;
    }
  }

  async function hydrateSearch() {
    const query = router.currentRoute.value.query;
    state.value.favoritesOnly = isOwnGroup.value && query.favoritesOnly === "true";
    state.value.auto = query.auto !== "false";
    if (query.search?.length) {
      state.value.search = query.search as string;
    }
    else {
      state.value.search = queryDefaults.search;
    }

    const requestedOrder = typeof query.orderBy === "string" ? query.orderBy : sortPreferences.value.orderBy;
    state.value.orderBy = recipeSortOptions.some(([field]) => field === requestedOrder) && (isOwnGroup.value || requestedOrder !== "last_made") ? requestedOrder : queryDefaults.orderBy;
    const requestedDirection = query.orderDirection || sortPreferences.value.orderDirection;
    state.value.orderDirection = requestedDirection === "asc" ? "asc" : "desc";

    if (query.requireAllCategories?.length) {
      state.value.requireAllCategories = query.requireAllCategories === "true";
    }
    else {
      state.value.requireAllCategories = queryDefaults.requireAllCategories;
    }

    if (query.requireAllTags?.length) {
      state.value.requireAllTags = query.requireAllTags === "true";
    }
    else {
      state.value.requireAllTags = queryDefaults.requireAllTags;
    }

    if (query.requireAllTools?.length) {
      state.value.requireAllTools = query.requireAllTools === "true";
    }
    else {
      state.value.requireAllTools = queryDefaults.requireAllTools;
    }

    if (query.requireAllFoods?.length) {
      state.value.requireAllFoods = query.requireAllFoods === "true";
    }
    else {
      state.value.requireAllFoods = queryDefaults.requireAllFoods;
    }

    const promises: Promise<void>[] = [];

    if (query.categories?.length) {
      promises.push(
        waitUntilAndExecute(
          () => categories.store.value.length > 0,
          () => {
            const result = categories.store.value.filter(item =>
              (query.categories as string[]).includes(item.id as string),
            );
            selectedCategories.value = result;
          },
        ),
      );
    }
    else {
      selectedCategories.value = [];
    }

    if (query.tags?.length) {
      promises.push(
        waitUntilAndExecute(
          () => tags.store.value.length > 0,
          () => {
            const result = tags.store.value.filter(item => (query.tags as string[]).includes(item.id as string));
            selectedTags.value = result;
          },
        ),
      );
    }
    else {
      selectedTags.value = [];
    }

    if (query.tools?.length) {
      promises.push(
        waitUntilAndExecute(
          () => tools.store.value.length > 0,
          () => {
            const result = tools.store.value.filter(item => (query.tools as string[]).includes(item.id));
            selectedTools.value = result;
          },
        ),
      );
    }
    else {
      selectedTools.value = [];
    }

    if (query.foods?.length) {
      promises.push(
        waitUntilAndExecute(
          () => {
            if (foods.store.value) {
              return foods.store.value.length > 0;
            }
            return false;
          },
          () => {
            const result = foods.store.value?.filter(item => (query.foods as string[]).includes(item.id));
            selectedFoods.value = result ?? [];
          },
        ),
      );
    }
    else {
      selectedFoods.value = [];
    }

    if (query.households?.length) {
      promises.push(
        waitUntilAndExecute(
          () => {
            if (households.store.value) {
              return households.store.value.length > 0;
            }
            return false;
          },
          () => {
            const result = households.store.value?.filter(item => (query.households as string[]).includes(item.id));
            selectedHouseholds.value = result as NoUndefinedField<HouseholdSummary>[] ?? [];
          },
        ),
      );
    }
    else {
      selectedHouseholds.value = [];
    }

    await Promise.allSettled(promises);
  }

  async function initialize() {
    // Restore the user's last search query
    if (searchQuerySession.value.recipe && !(Object.keys(route.query).length > 0)) {
      try {
        const query = JSON.parse(searchQuerySession.value.recipe);
        await router.replace({ query });
      }
      catch {
        searchQuerySession.value.recipe = "";
        router.replace({ query: {} });
      }
    }

    await hydrateSearch();
    await search();
    state.value.ready = true;
  }

  // Restore search and filters on browser history navigation.
  watch(() => route.query, async () => {
    if (!state.value.ready || updatingRoute) return;
    hydrating = true;
    try {
      await hydrateSearch();
      passedQuery.value = calcPassedQuery();
      searchQuerySession.value.recipe = JSON.stringify(route.query);
    }
    finally {
      hydrating = false;
    }
  });

  // Auto-search when parameters change
  watchDebounced(
    [
      () => state.value.favoritesOnly,
      () => state.value.randomSeed,
      () => state.value.search,
      () => state.value.requireAllCategories,
      () => state.value.requireAllTags,
      () => state.value.requireAllTools,
      () => state.value.requireAllFoods,
      () => state.value.orderBy,
      () => state.value.orderDirection,
      selectedCategories,
      selectedFoods,
      selectedHouseholds,
      selectedTags,
      selectedTools,
    ],
    async () => {
      if (state.value.ready && state.value.auto && !hydrating) {
        await search();
      }
    },
    {
      debounce: 500,
    },
  );

  const composableInstance: RecipeExplorerSearchState = {
    // State
    state,
    selectedCategories,
    selectedFoods,
    selectedHouseholds,
    selectedTags,
    selectedTools,

    // Computed
    passedQueryWithSeed,

    // Methods
    search,
    reset,
    clearFilters,
    toggleOrderDirection,
    setOrderBy,
    setRandomOrderBy,
    filterItems,
    initialize,
  };

  return composableInstance;
}

export function useRecipeExplorerSearch(groupSlug: ComputedRef<string>): RecipeExplorerSearchState {
  const key = groupSlug.value;

  if (!memo[key]) {
    memo[key] = createRecipeExplorerSearchState(groupSlug);
  }

  return memo[key];
}

export function clearRecipeExplorerSearchState(groupSlug: string) {
  // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
  delete memo[groupSlug];
}
