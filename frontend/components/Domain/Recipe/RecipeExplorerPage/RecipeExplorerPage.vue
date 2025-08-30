<template>
  <v-container
    fluid
    class="px-0"
  >
    <RecipeExplorerPageSearch
      v-model:search="state.search"
      v-model:order-by="state.orderBy"
      v-model:order-direction="state.orderDirection"
      v-model:auto="state.auto"
      v-model:require-all-categories="state.requireAllCategories"
      v-model:require-all-tags="state.requireAllTags"
      v-model:require-all-tools="state.requireAllTools"
      v-model:require-all-foods="state.requireAllFoods"
      v-model:selected-categories="selectedCategories"
      v-model:selected-tags="selectedTags"
      v-model:selected-tools="selectedTools"
      v-model:selected-foods="selectedFoods"
      v-model:selected-households="selectedHouseholds"
      @search="search"
      @reset="reset"
      @toggle-order-direction="toggleOrderDirection"
      @set-order-by="setOrderBy"
    />
    <v-divider />
    <v-container class="mt-6 px-md-6">
      <RecipeCardSection
        v-if="state.ready"
        class="mt-n5"
        :icon="$globals.icons.silverwareForkKnife"
        :title="$t('general.recipes')"
        :recipes="recipes"
        :query="passedQueryWithSeed"
        disable-sort
        @item-selected="filterItems"
        @replace-recipes="replaceRecipes"
        @append-recipes="appendRecipes"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { watchDebounced } from "@vueuse/shared";
import { useLoggedInState } from "~/composables/use-logged-in-state";
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
import { useUserSearchQuerySession, useUserSortPreferences } from "~/composables/use-users/preferences";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import RecipeExplorerPageSearch from "./RecipeExplorerPageParts/RecipeExplorerPageSearch.vue";
import type { IngredientFood, RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useLazyRecipes } from "~/composables/recipes";
import type { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";
import type { HouseholdSummary } from "~/lib/api/types/household";

export default defineNuxtComponent({
  components: { RecipeCardSection, RecipeExplorerPageSearch },
  setup() {
    const router = useRouter();
    const $auth = useMealieAuth();

    const { isOwnGroup } = useLoggedInState();
    const state = ref({
      auto: true,
      ready: false,
      search: "",
      orderBy: "created_at",
      orderDirection: "desc" as "asc" | "desc",

      // and/or
      requireAllCategories: false,
      requireAllTags: false,
      requireAllTools: false,
      requireAllFoods: false,
    });

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const searchQuerySession = useUserSearchQuerySession();
    const sortPreferences = useUserSortPreferences();

    watch(() => state.value.orderBy, (newValue) => {
      sortPreferences.value.orderBy = newValue;
    });

    watch(() => state.value.orderDirection, (newValue) => {
      sortPreferences.value.orderDirection = newValue;
    });

    const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes(isOwnGroup.value ? null : groupSlug.value);
    const categories = isOwnGroup.value ? useCategoryStore() : usePublicCategoryStore(groupSlug.value);
    const selectedCategories = ref<NoUndefinedField<RecipeCategory>[]>([]);

    const foods = isOwnGroup.value ? useFoodStore() : usePublicFoodStore(groupSlug.value);
    const selectedFoods = ref<IngredientFood[]>([]);

    const households = isOwnGroup.value ? useHouseholdStore() : usePublicHouseholdStore(groupSlug.value);
    const selectedHouseholds = ref([] as NoUndefinedField<HouseholdSummary>[]);

    const tags = isOwnGroup.value ? useTagStore() : usePublicTagStore(groupSlug.value);
    const selectedTags = ref<NoUndefinedField<RecipeTag>[]>([]);

    const tools = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);
    const selectedTools = ref<NoUndefinedField<RecipeTool>[]>([]);

    function calcPassedQuery(): RecipeSearchQuery {
      return {
        // the search clear button sets search to null, which still renders the query param for a moment,
        // whereas an empty string is not rendered
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
        orderBy: state.value.orderBy,
        orderDirection: state.value.orderDirection,
      };
    }
    const passedQuery = ref<RecipeSearchQuery>(calcPassedQuery());

    // we calculate this separately because otherwise we can't check for query changes
    const passedQueryWithSeed = computed(() => {
      return {
        ...passedQuery.value,
        _searchSeed: Date.now().toString(),
      };
    });

    const queryDefaults = {
      search: "",
      orderBy: "created_at",
      orderDirection: "desc" as "asc" | "desc",
      requireAllCategories: false,
      requireAllTags: false,
      requireAllTools: false,
      requireAllFoods: false,
    };

    function reset() {
      state.value.search = queryDefaults.search;
      state.value.orderBy = queryDefaults.orderBy;
      state.value.orderDirection = queryDefaults.orderDirection;
      sortPreferences.value.orderBy = queryDefaults.orderBy;
      sortPreferences.value.orderDirection = queryDefaults.orderDirection;
      state.value.requireAllCategories = queryDefaults.requireAllCategories;
      state.value.requireAllTags = queryDefaults.requireAllTags;
      state.value.requireAllTools = queryDefaults.requireAllTools;
      state.value.requireAllFoods = queryDefaults.requireAllFoods;
      selectedCategories.value = [];
      selectedFoods.value = [];
      selectedHouseholds.value = [];
      selectedTags.value = [];
      selectedTools.value = [];
    }

    function toggleOrderDirection() {
      state.value.orderDirection = state.value.orderDirection === "asc" ? "desc" : "asc";
      sortPreferences.value.orderDirection = state.value.orderDirection;
    }

    function setOrderBy(value: string) {
      state.value.orderBy = value;
      sortPreferences.value.orderBy = value;
    }

    function toIDArray(array: { id: string }[]) {
      // we sort the array to make sure the query is always the same
      return array.map(item => item.id).sort();
    }

    async function search() {
      const oldQueryValueString = JSON.stringify(passedQuery.value);
      const newQueryValue = calcPassedQuery();
      const newQueryValueString = JSON.stringify(newQueryValue);
      if (oldQueryValueString === newQueryValueString) {
        return;
      }

      passedQuery.value = newQueryValue;
      const query = {
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
      await router.push({ query });
      searchQuerySession.value.recipe = JSON.stringify(query);
    }

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

        // For some reason these were returning NodeJS.Timeout
        state.interval = setInterval(check, opts.interval) as unknown as number;
        state.timeout = setTimeout(() => {
          clearInterval(state.interval);
          reject(new Error("Timeout"));
        }, opts.timeout) as unknown as number;
      });
    }

    watch(
      () => route.query,
      () => {
        if (!Object.keys(route.query).length) {
          reset();
        }
      },
    );

    function filterItems(item: RecipeCategory | RecipeTag | RecipeTool, urlPrefix: string) {
      if (urlPrefix === "categories") {
        const result = categories.store.value.filter(category => (category.id as string).includes(item.id as string));
        selectedCategories.value = result as NoUndefinedField<RecipeTag>[];
      }
      else if (urlPrefix === "tags") {
        const result = tags.store.value.filter(tag => (tag.id as string).includes(item.id as string));
        selectedTags.value = result as NoUndefinedField<RecipeTag>[];
      }
      else if (urlPrefix === "tools") {
        const result = tools.store.value.filter(tool => (tool.id).includes(item.id || ""));
        selectedTags.value = result as NoUndefinedField<RecipeTag>[];
      }
    }

    async function hydrateSearch() {
      const query = router.currentRoute.value.query;
      if (query.auto?.length) {
        state.value.auto = query.auto === "true";
      }

      if (query.search?.length) {
        state.value.search = query.search as string;
      }
      else {
        state.value.search = queryDefaults.search;
      }

      state.value.orderBy = sortPreferences.value.orderBy;
      state.value.orderDirection = sortPreferences.value.orderDirection as "asc" | "desc";

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

              selectedCategories.value = result as NoUndefinedField<RecipeCategory>[];
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
              selectedTags.value = result as NoUndefinedField<RecipeTag>[];
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
              selectedTools.value = result as NoUndefinedField<RecipeTool>[];
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
    };

    onMounted(async () => {
      // restore the user's last search query
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
    });

    watchDebounced(
      [
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
        if (state.value.ready && state.value.auto) {
          await search();
        }
      },
      {
        debounce: 500,
      },
    );

    return {
      search,
      reset,
      state,

      toggleOrderDirection,
      setOrderBy,

      selectedCategories,
      selectedFoods,
      selectedHouseholds,
      selectedTags,
      selectedTools,
      appendRecipes,
      assignSorted,
      recipes,
      removeRecipe,
      replaceRecipes,
      passedQueryWithSeed,

      filterItems,
    };
  },
});
</script>
