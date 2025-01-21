<template>
  <v-container fluid class="pa-0">
    <div class="search-container py-8">
      <form class="search-box pa-2" @submit.prevent="search">
        <div class="d-flex justify-center my-2">
          <v-text-field
            ref="input"
            v-model="state.search"
            outlined
            hide-details
            clearable
            color="primary"
            :placeholder="$tc('search.search-placeholder')"
            :prepend-inner-icon="$globals.icons.search"
            @keyup.enter="hideKeyboard"
          />
        </div>
        <div class="search-row">
          <!-- Category Filter -->
          <SearchFilter
            v-if="categories"
            v-model="selectedCategories"
            :require-all.sync="state.requireAllCategories"
            :items="categories"
          >
            <v-icon left>
              {{ $globals.icons.categories }}
            </v-icon>
            {{ $t("category.categories") }}
          </SearchFilter>

          <!-- Tag Filter -->
          <SearchFilter v-if="tags" v-model="selectedTags" :require-all.sync="state.requireAllTags" :items="tags">
            <v-icon left>
              {{ $globals.icons.tags }}
            </v-icon>
            {{ $t("tag.tags") }}
          </SearchFilter>

          <!-- Tool Filter -->
          <SearchFilter v-if="tools" v-model="selectedTools" :require-all.sync="state.requireAllTools" :items="tools">
            <v-icon left>
              {{ $globals.icons.potSteam }}
            </v-icon>
            {{ $t("tool.tools") }}
          </SearchFilter>

          <!-- Food Filter -->
          <SearchFilter v-if="foods" v-model="selectedFoods" :require-all.sync="state.requireAllFoods" :items="foods">
            <v-icon left>
              {{ $globals.icons.foods }}
            </v-icon>
            {{ $t("general.foods") }}
          </SearchFilter>

          <!-- Household Filter -->
          <SearchFilter v-if="households.length > 1" v-model="selectedHouseholds" :items="households" radio>
            <v-icon left>
              {{ $globals.icons.household }}
            </v-icon>
            {{ $t("household.households") }}
          </SearchFilter>

          <!-- Sort Options -->
          <v-menu offset-y nudge-bottom="3">
            <template #activator="{ on, attrs }">
              <v-btn class="ml-auto" small color="accent" v-bind="attrs" v-on="on">
                <v-icon :left="!$vuetify.breakpoint.xsOnly">
                  {{ state.orderDirection === "asc" ? $globals.icons.sortAscending : $globals.icons.sortDescending }}
                </v-icon>
                {{ $vuetify.breakpoint.xsOnly ? null : sortText }}
              </v-btn>
            </template>
            <v-card>
              <v-list>
                <v-list-item @click="toggleOrderDirection()">
                  <v-icon left>
                    {{
                      state.orderDirection === "asc" ?
                      $globals.icons.sortDescending : $globals.icons.sortAscending
                    }}
                  </v-icon>
                  <v-list-item-title>
                    {{ state.orderDirection === "asc" ? $tc("general.sort-descending") : $tc("general.sort-ascending") }}
                  </v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  v-for="v in sortable"
                  :key="v.name"
                  :input-value="state.orderBy === v.value"
                  @click="state.orderBy = v.value"
                >
                  <v-icon left>
                    {{ v.icon }}
                  </v-icon>
                  <v-list-item-title>{{ v.name }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>

          <!-- Settings -->
          <v-menu offset-y bottom left nudge-bottom="3" :close-on-content-click="false">
            <template #activator="{ on, attrs }">
              <v-btn small color="accent" dark v-bind="attrs" v-on="on">
                <v-icon small>
                  {{ $globals.icons.cog }}
                </v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-text>
                <v-switch v-model="state.auto" :label="$t('search.auto-search')" single-line></v-switch>
                <v-btn block color="primary" @click="reset">
                  {{ $tc("general.reset") }}
                </v-btn>
              </v-card-text>
            </v-card>
          </v-menu>
        </div>
        <div v-if="!state.auto" class="search-button-container">
          <v-btn x-large color="primary" type="submit" block>
            <v-icon left>
              {{ $globals.icons.search }}
            </v-icon>
            {{ $tc("search.search") }}
          </v-btn>
        </div>
      </form>
    </div>
    <v-divider></v-divider>
    <v-container class="mt-6 px-md-6">
      <RecipeCardSection
        v-if="state.ready"
        class="mt-n5"
        :icon="$globals.icons.silverwareForkKnife"
        :title="$tc('general.recipes')"
        :recipes="recipes"
        :query="passedQueryWithSeed"
        @item-selected="filterItems"
        @replaceRecipes="replaceRecipes"
        @appendRecipes="appendRecipes"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { ref, defineComponent, useRouter, onMounted, useContext, computed, Ref, useRoute, watch } from "@nuxtjs/composition-api";
import { watchDebounced } from "@vueuse/shared";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
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
import { useUserSearchQuerySession } from "~/composables/use-users/preferences";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { IngredientFood, RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useLazyRecipes } from "~/composables/recipes";
import { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";
import { HouseholdSummary } from "~/lib/api/types/household";

export default defineComponent({
  components: { SearchFilter, RecipeCardSection },
  setup() {
    const router = useRouter();
    const { $auth, $globals, i18n } = useContext();

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
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const searchQuerySession = useUserSearchQuerySession();

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
        _searchSeed: Date.now().toString()
      };
    })

    const queryDefaults = {
      search: "",
      orderBy: "created_at",
      orderDirection: "desc" as "asc" | "desc",
      requireAllCategories: false,
      requireAllTags: false,
      requireAllTools: false,
      requireAllFoods: false,
    }

    function reset() {
      state.value.search = queryDefaults.search;
      state.value.orderBy = queryDefaults.orderBy;
      state.value.orderDirection = queryDefaults.orderDirection;
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
    }

    function toIDArray(array: { id: string }[]) {
      // we sort the array to make sure the query is always the same
      return array.map((item) => item.id).sort();
    }

    function hideKeyboard() {
      input.value.blur()
    }

    const input: Ref<any> = ref(null);

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
          orderBy: passedQuery.value.orderBy === queryDefaults.orderBy ? undefined : passedQuery.value.orderBy,
          orderDirection: passedQuery.value.orderDirection === queryDefaults.orderDirection ? undefined : passedQuery.value.orderDirection,
          households: !passedQuery.value.households?.length || passedQuery.value.households?.length === households.store.value.length ? undefined : passedQuery.value.households,
          requireAllCategories: passedQuery.value.requireAllCategories ? "true" : undefined,
          requireAllTags: passedQuery.value.requireAllTags ? "true" : undefined,
          requireAllTools: passedQuery.value.requireAllTools ? "true" : undefined,
          requireAllFoods: passedQuery.value.requireAllFoods ? "true" : undefined,
        },
      }
      await router.push({ query });
      searchQuerySession.value.recipe = JSON.stringify(query);
    }

    function waitUntilAndExecute(
      condition: () => boolean,
      callback: () => void,
      opts = { timeout: 2000, interval: 500 }
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

    const sortText = computed(() => {
      const sort = sortable.find((s) => s.value === state.value.orderBy);
      if (!sort) return "";
      return `${sort.name}`;
    });

    const sortable = [
      {
        icon: $globals.icons.orderAlphabeticalAscending,
        name: i18n.tc("general.sort-alphabetically"),
        value: "name",
      },
      {
        icon: $globals.icons.newBox,
        name: i18n.tc("general.created"),
        value: "created_at",
      },
      {
        icon: $globals.icons.chefHat,
        name: i18n.tc("general.last-made"),
        value: "last_made",
      },
      {
        icon: $globals.icons.star,
        name: i18n.tc("general.rating"),
        value: "rating",
      },
      {
        icon: $globals.icons.update,
        name: i18n.tc("general.updated"),
        value: "updated_at",
      },
      {
        icon: $globals.icons.diceMultiple,
        name: i18n.tc("general.random"),
        value: "random",
      },
    ];

    watch(
      () => route.value.query,
      () => {
        if (!Object.keys(route.value.query).length) {
          reset();
        }
      }
    )

    function filterItems(item: RecipeCategory | RecipeTag | RecipeTool, urlPrefix: string) {
      if (urlPrefix === "categories") {
        const result = categories.store.value.filter((category) => (category.id as string).includes(item.id as string));
        selectedCategories.value = result as NoUndefinedField<RecipeTag>[];
      } else if (urlPrefix === "tags") {
        const result = tags.store.value.filter((tag) => (tag.id as string).includes(item.id as string));
        selectedTags.value = result as NoUndefinedField<RecipeTag>[];
      } else if (urlPrefix === "tools") {
        const result = tools.store.value.filter((tool) => (tool.id ).includes(item.id || "" ));
        selectedTags.value = result as NoUndefinedField<RecipeTag>[];
      }
    }

    async function hydrateSearch() {
      const query = router.currentRoute.query;
      if (query.auto?.length) {
        state.value.auto = query.auto === "true";
      }

      if (query.search?.length) {
        state.value.search = query.search as string;
      } else {
        state.value.search = queryDefaults.search;
      }

      if (query.orderBy?.length) {
        state.value.orderBy = query.orderBy as string;
      } else {
        state.value.orderBy = queryDefaults.orderBy;
      }

      if (query.orderDirection?.length) {
        state.value.orderDirection = query.orderDirection as "asc" | "desc";
      } else {
        state.value.orderDirection = queryDefaults.orderDirection;
      }

      if (query.requireAllCategories?.length) {
        state.value.requireAllCategories = query.requireAllCategories === "true";
      } else {
        state.value.requireAllCategories = queryDefaults.requireAllCategories;
      }

      if (query.requireAllTags?.length) {
        state.value.requireAllTags = query.requireAllTags === "true";
      } else {
        state.value.requireAllTags = queryDefaults.requireAllTags;
      }

      if (query.requireAllTools?.length) {
        state.value.requireAllTools = query.requireAllTools === "true";
      } else {
        state.value.requireAllTools = queryDefaults.requireAllTools;
      }

      if (query.requireAllFoods?.length) {
        state.value.requireAllFoods = query.requireAllFoods === "true";
      } else {
        state.value.requireAllFoods = queryDefaults.requireAllFoods;
      }

      const promises: Promise<void>[] = [];

      if (query.categories?.length) {
        promises.push(
          waitUntilAndExecute(
            () => categories.store.value.length > 0,
            () => {
              const result = categories.store.value.filter((item) =>
                (query.categories as string[]).includes(item.id as string)
              );

              selectedCategories.value = result as NoUndefinedField<RecipeCategory>[];
            }
          )
        );
      } else {
        selectedCategories.value = [];
      }

      if (query.tags?.length) {
        promises.push(
          waitUntilAndExecute(
            () => tags.store.value.length > 0,
            () => {
              const result = tags.store.value.filter((item) => (query.tags as string[]).includes(item.id as string));
              selectedTags.value = result as NoUndefinedField<RecipeTag>[];
            }
          )
        );
      } else {
        selectedTags.value = [];
      }

      if (query.tools?.length) {
        promises.push(
          waitUntilAndExecute(
            () => tools.store.value.length > 0,
            () => {
              const result = tools.store.value.filter((item) => (query.tools as string[]).includes(item.id));
              selectedTools.value = result as NoUndefinedField<RecipeTool>[];
            }
          )
        );
      } else {
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
              const result = foods.store.value?.filter((item) => (query.foods as string[]).includes(item.id));
              selectedFoods.value = result ?? [];
            }
          )
        );
      } else {
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
              const result = households.store.value?.filter((item) => (query.households as string[]).includes(item.id));
              selectedHouseholds.value = result as NoUndefinedField<HouseholdSummary>[] ?? [];
            }
          )
        );
      } else {
        selectedHouseholds.value = [];
      }

      await Promise.allSettled(promises);
    };

    onMounted(async () => {
      // restore the user's last search query
      if (searchQuerySession.value.recipe && !(Object.keys(route.value.query).length > 0)) {
        try {
          const query = JSON.parse(searchQuerySession.value.recipe);
          await router.replace({ query });
        } catch (error) {
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
      }
    );

    return {
      sortText,
      search,
      reset,
      state,
      categories: categories.store as unknown as NoUndefinedField<RecipeCategory>[],
      tags: tags.store as unknown as NoUndefinedField<RecipeTag>[],
      foods: foods.store,
      tools: tools.store as unknown as NoUndefinedField<RecipeTool>[],
      households: households.store as unknown as NoUndefinedField<HouseholdSummary>[],

      sortable,
      toggleOrderDirection,
      hideKeyboard,
      input,

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
  head: {},
});
</script>

<style lang="css">
.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 1rem;
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-box {
  width: 950px;
}

.search-button-container {
  margin: 3rem auto 0 auto;
  max-width: 500px;
}
</style>
