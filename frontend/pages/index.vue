<template>
  <v-container fluid class="pa-0">
    <div class="search-container py-8">
      <form class="search-box pa-2" @submit.prevent="search">
        <div class="d-flex justify-center my-2">
          <v-text-field
            v-model="state.search"
            outlined
            autofocus
            hide-details
            clearable
            color="primary"
            :placeholder="$tc('search.search-placeholder')"
            :prepend-inner-icon="$globals.icons.search"
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
              {{ $globals.icons.tags }}
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
              {{ $globals.icons.tools }}
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
                    {{ $globals.icons.sort }}
                  </v-icon>
                  <v-list-item-title>
                    {{ state.orderDirection === "asc" ? "Sort Descending" : "Sort Ascending" }}
                  </v-list-item-title>
                </v-list-item>
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
        class="mt-n5"
        :icon="$globals.icons.search"
        :title="$tc('search.results')"
        :recipes="recipes"
        :query="passedQuery"
        @replaceRecipes="replaceRecipes"
        @appendRecipes="appendRecipes"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { ref, defineComponent, useRouter, onMounted, useContext, computed } from "@nuxtjs/composition-api";
import { watchDebounced } from "@vueuse/shared";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { useCategoryStore, useFoodStore, useTagStore, useToolStore } from "~/composables/store";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { IngredientFood, RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { useLazyRecipes } from "~/composables/recipes";
import { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";

export default defineComponent({
  components: { SearchFilter, RecipeCardSection },
  setup() {
    const { recipes, appendRecipes, assignSorted, removeRecipe, replaceRecipes } = useLazyRecipes();

    const router = useRouter();
    const { $globals, i18n } = useContext();

    const state = ref({
      auto: true,
      search: "",
      orderBy: "created_at",
      orderDirection: "desc" as "asc" | "desc",

      // and/or
      requireAllCategories: false,
      requireAllTags: false,
      requireAllTools: false,
      requireAllFoods: false,
    });

    const categories = useCategoryStore();
    const selectedCategories = ref<NoUndefinedField<RecipeCategory>[]>([]);

    const foods = useFoodStore();
    const selectedFoods = ref<IngredientFood[]>([]);

    const tags = useTagStore();
    const selectedTags = ref<NoUndefinedField<RecipeTag>[]>([]);

    const tools = useToolStore();
    const selectedTools = ref<NoUndefinedField<RecipeTool>[]>([]);

    const passedQuery = ref<RecipeSearchQuery | null>(null);

    function reset() {
      state.value.search = "";
      state.value.orderBy = "created_at";
      state.value.orderDirection = "desc";
      state.value.requireAllCategories = false;
      state.value.requireAllTags = false;
      state.value.requireAllTools = false;
      state.value.requireAllFoods = false;
      selectedCategories.value = [];
      selectedFoods.value = [];
      selectedTags.value = [];
      selectedTools.value = [];

      router.push({
        query: {},
      });

      search();
    }

    function toggleOrderDirection() {
      state.value.orderDirection = state.value.orderDirection === "asc" ? "desc" : "asc";
    }

    function toIDArray(array: { id: string }[]) {
      return array.map((item) => item.id);
    }

    async function search() {
      await router.push({
        query: {
          categories: toIDArray(selectedCategories.value),
          foods: toIDArray(selectedFoods.value),
          tags: toIDArray(selectedTags.value),
          tools: toIDArray(selectedTools.value),
          // Only add the query param if it's or not default
          ...{
            auto: state.value.auto ? undefined : "false",
            search: state.value.search === "" ? undefined : state.value.search,
            orderBy: state.value.orderBy === "createdAt" ? undefined : state.value.orderBy,
            orderDirection: state.value.orderDirection === "desc" ? undefined : state.value.orderDirection,
            requireAllCategories: state.value.requireAllCategories ? "true" : undefined,
            requireAllTags: state.value.requireAllTags ? "true" : undefined,
            requireAllTools: state.value.requireAllTools ? "true" : undefined,
            requireAllFoods: state.value.requireAllFoods ? "true" : undefined,
          },
        },
      });

      passedQuery.value = {
        search: state.value.search,
        categories: toIDArray(selectedCategories.value),
        foods: toIDArray(selectedFoods.value),
        tags: toIDArray(selectedTags.value),
        tools: toIDArray(selectedTools.value),
        requireAllCategories: state.value.requireAllCategories,
        requireAllTags: state.value.requireAllTags,
        requireAllTools: state.value.requireAllTools,
        requireAllFoods: state.value.requireAllFoods,
        orderBy: state.value.orderBy,
        orderDirection: state.value.orderDirection,
        _searchSeed: Date.now().toString()
      };
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
        value: "update_at",
      },
      {
        icon: $globals.icons.diceMultiple,
        name: i18n.tc("general.random"),
        value: "random",
      },
    ];

    onMounted(() => {
      // Hydrate Search
      // wait for stores to be hydrated

      // read query params
      const query = router.currentRoute.query;

      if (query.auto) {
        state.value.auto = query.auto === "true";
      }

      if (query.search) {
        state.value.search = query.search as string;
      }

      if (query.orderBy) {
        state.value.orderBy = query.orderBy as string;
      }

      if (query.orderDirection) {
        state.value.orderDirection = query.orderDirection as "asc" | "desc";
      }

      const promises: Promise<void>[] = [];

      if (query.categories) {
        promises.push(
          waitUntilAndExecute(
            () => categories.items.value.length > 0,
            () => {
              const result = categories.items.value.filter((item) =>
                (query.categories as string[]).includes(item.id as string)
              );

              selectedCategories.value = result as NoUndefinedField<RecipeCategory>[];
            }
          )
        );
      }

      if (query.foods) {
        promises.push(
          waitUntilAndExecute(
            () => {
              if (foods.foods.value) {
                return foods.foods.value.length > 0;
              }
              return false;
            },
            () => {
              const result = foods.foods.value?.filter((item) => (query.foods as string[]).includes(item.id));
              selectedFoods.value = result ?? [];
            }
          )
        );
      }

      if (query.tags) {
        promises.push(
          waitUntilAndExecute(
            () => tags.items.value.length > 0,
            () => {
              const result = tags.items.value.filter((item) => (query.tags as string[]).includes(item.id as string));
              selectedTags.value = result as NoUndefinedField<RecipeTag>[];
            }
          )
        );
      }

      if (query.tools) {
        promises.push(
          waitUntilAndExecute(
            () => tools.items.value.length > 0,
            () => {
              const result = tools.items.value.filter((item) => (query.tools as string[]).includes(item.id));
              selectedTools.value = result as NoUndefinedField<RecipeTool>[];
            }
          )
        );
      }

      Promise.allSettled(promises).then(() => {
        search();
      });
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
        selectedTags,
        selectedTools,
      ],
      async () => {
        if (state.value.auto) {
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
      categories: categories.items as unknown as NoUndefinedField<RecipeCategory>[],
      tags: tags.items as unknown as NoUndefinedField<RecipeTag>[],
      foods: foods.foods,
      tools: tools.items as unknown as NoUndefinedField<RecipeTool>[],

      sortable,
      toggleOrderDirection,

      selectedCategories,
      selectedFoods,
      selectedTags,
      selectedTools,
      appendRecipes,
      assignSorted,
      recipes,
      removeRecipe,
      replaceRecipes,
      passedQuery,
    };
  },
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
