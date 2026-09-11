<template>
  <div
    class="recipe-selector d-flex flex-column"
    :style="{ height }"
  >
    <!-- v-input defaults to flex-grow, which stretches the field when the results are short -->
    <v-text-field
      v-model="search"
      class="flex-grow-0"
      variant="outlined"
      density="compact"
      color="primary"
      autofocus
      hide-details
      clearable
      :placeholder="$t('search.search-placeholder')"
      :prepend-inner-icon="$globals.icons.search"
    />

    <div class="d-flex flex-wrap align-start ga-2 mt-3">
      <SearchFilter
        v-if="categories.length"
        v-model="selectedCategories"
        :items="categories"
      >
        <v-icon start>
          {{ $globals.icons.categories }}
        </v-icon>
        {{ $t("category.categories") }}
      </SearchFilter>
      <SearchFilter
        v-if="tags.length"
        v-model="selectedTags"
        :items="tags"
      >
        <v-icon start>
          {{ $globals.icons.tags }}
        </v-icon>
        {{ $t("tag.tags") }}
      </SearchFilter>
      <slot name="filters" />
    </div>

    <div
      v-if="modelValue"
      class="d-flex align-center ga-2 mt-3"
    >
      <span class="text-caption text-medium-emphasis">{{ $t("general.selected") }}</span>
      <v-chip
        label
        color="primary"
        closable
        :prepend-icon="$globals.icons.silverwareForkKnife"
        @click:close="select(null)"
      >
        {{ modelValue.name }}
      </v-chip>
    </div>

    <div
      ref="resultsContainer"
      class="recipe-results mt-3"
    >
      <v-list
        v-if="recipes.length"
        class="py-0"
      >
        <RecipeCardLineItem
          v-for="recipe in recipes"
          :key="recipe.id!"
          :recipe="recipe"
          :active="recipe.id === modelValue?.id"
          disable-link
          @click="select(recipe)"
        />
      </v-list>

      <div
        v-else-if="!loading"
        class="py-2"
      >
        <slot name="no-results">
          <v-alert
            type="info"
            variant="tonal"
            :text="$t('search.no-results')"
          />
        </slot>
      </div>

      <div ref="sentinel" />

      <v-progress-circular
        v-if="loading"
        indeterminate
        color="primary"
        class="d-block mx-auto my-3"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useIntersectionObserver, watchDebounced } from "@vueuse/core";
import RecipeCardLineItem from "./RecipeCardLineItem.vue";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { useLazyRecipes } from "~/composables/recipes";
import { useCategoryStore, useTagStore } from "~/composables/store";
import type { Recipe, RecipeCategory, RecipeSummary, RecipeTag } from "~/lib/api/types/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";

interface Props {
  queryFilter?: string | null;
  height?: string;
}
const props = withDefaults(defineProps<Props>(), {
  queryFilter: null,
  height: "100%",
});

const modelValue = defineModel<RecipeSummary | null>({ default: null });

const PER_PAGE = 20;

const { fetchMore } = useLazyRecipes();
const { store: categories } = useCategoryStore();
const { store: tags } = useTagStore();

const search = ref("");
const selectedCategories = ref<NoUndefinedField<RecipeCategory>[]>([]);
const selectedTags = ref<NoUndefinedField<RecipeTag>[]>([]);

const recipes = ref<Recipe[]>([]);
const page = ref(1);
const hasMore = ref(true);
const loading = ref(false);

// discards the results of any request that was superseded while it was in flight
let latestRequest = 0;

const query = computed<RecipeSearchQuery>(() => {
  return {
    search: search.value || "",
    categories: selectedCategories.value.map(category => category.id),
    tags: selectedTags.value.map(tag => tag.id),
  };
});

function select(recipe: RecipeSummary | null) {
  modelValue.value = recipe;
}

function reset() {
  search.value = "";
  selectedCategories.value = [];
  selectedTags.value = [];
}

defineExpose({ reset });

async function fetchPage(pageNumber: number, perPage: number) {
  return await fetchMore(pageNumber, perPage, "name", "asc", null, query.value, props.queryFilter);
}

async function reload() {
  const requestId = ++latestRequest;
  loading.value = true;

  // we double-up the first call so the results overflow their container,
  // otherwise there's nothing to scroll and no more recipes are ever loaded
  const newRecipes = await fetchPage(1, PER_PAGE * 2);
  if (requestId !== latestRequest) {
    return;
  }

  recipes.value = newRecipes;
  hasMore.value = newRecipes.length >= PER_PAGE * 2;
  page.value = 2;
  loading.value = false;
}

async function loadMore() {
  if (!hasMore.value || loading.value) {
    return;
  }

  const requestId = ++latestRequest;
  loading.value = true;
  page.value += 1;

  const newRecipes = await fetchPage(page.value, PER_PAGE);
  if (requestId !== latestRequest) {
    return;
  }

  recipes.value = [...recipes.value, ...newRecipes];
  hasMore.value = newRecipes.length >= PER_PAGE;
  loading.value = false;
}

const resultsContainer = ref<HTMLElement | null>(null);
const sentinel = ref<HTMLElement | null>(null);
useIntersectionObserver(
  sentinel,
  ([entry]) => {
    if (entry?.isIntersecting) {
      loadMore();
    }
  },
  { root: resultsContainer },
);

watchDebounced(
  [query, () => props.queryFilter],
  async () => {
    await reload();
  },
  { debounce: 300 },
);

onMounted(async () => {
  await reload();
});
</script>

<style scoped>
/* lets the results shrink when this is stretched by a flex parent */
.recipe-selector {
  min-height: 0;
}

.recipe-results {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}
</style>
