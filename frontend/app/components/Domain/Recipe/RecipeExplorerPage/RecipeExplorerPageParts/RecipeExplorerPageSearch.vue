<template>
  <div class="search-container">
    <form
      class="search-box"
      @submit.prevent="search"
    >
      <div class="search-row">
        <!-- Quick filters -->
        <button
          type="button"
          class="mealie-chip"
          :class="{ 'mealie-chip--active': !hasActiveFilters }"
          @click="reset"
        >
          {{ $t("recipe-library.all") }}
        </button>
        <RouterLink
          v-if="favoritesLink"
          :to="favoritesLink"
          class="mealie-chip"
        >
          {{ $t("general.favorites") }}
        </RouterLink>
        <button
          v-for="category in quickCategories"
          :key="category.id ?? category.slug"
          type="button"
          class="mealie-chip"
          :class="{ 'mealie-chip--active': isOnlyCategory(category.id) }"
          @click="toggleCategory(category)"
        >
          {{ category.name }}
        </button>

        <div class="search-row__spacer" />

        <RecipeExplorerPageSearchFilters />
        <!-- Sort Options -->
        <v-menu
          offset-y
          nudge-bottom="3"
        >
          <template #activator="{ props }">
            <v-btn
              size="small"
              variant="flat"
              rounded="pill"
              class="mealie-filter-btn"
              v-bind="props"
            >
              <v-icon :start="!$vuetify.display.xs">
                {{ state.orderDirection === "asc" ? $globals.icons.sortDescending : $globals.icons.sortAscending }}
              </v-icon>
              {{ $vuetify.display.xs ? null : sortText }}
            </v-btn>
          </template>
          <v-card>
            <v-list>
              <v-list-item
                slim
                density="comfortable"
                :prepend-icon="state.orderDirection === 'asc' ? $globals.icons.sortAscending : $globals.icons.sortDescending"
                :title="state.orderDirection === 'asc' ? $t('general.sort-descending') : $t('general.sort-ascending')"
                @click="toggleOrderDirection"
              />
              <v-divider />
              <v-list-item
                v-for="v in sortable"
                :key="v.name"
                :active="state.orderBy === v.value"
                slim
                density="comfortable"
                @click.stop="v.value === 'random' ? setRandomOrderByWrapper() : setOrderBy(v.value)"
              >
                <template #prepend>
                  <v-icon>{{ v.icon }}</v-icon>
                </template>

                <template #title>
                  <span>{{ v.name }}</span>
                  <v-icon
                    v-if="v.value === 'random' && showRandomLoading"
                    size="small"
                    class="ml-3"
                  >
                    {{ $globals.icons.refreshCircle }}
                  </v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </v-menu>

        <!-- Settings -->
        <v-menu
          offset-y
          bottom
          start
          nudge-bottom="3"
          :close-on-content-click="false"
        >
          <template #activator="{ props }">
            <v-btn
              size="small"
              variant="flat"
              rounded="pill"
              class="mealie-filter-btn"
              :aria-label="$t('general.settings')"
              v-bind="props"
            >
              <v-icon size="small">
                {{ $globals.icons.cog }}
              </v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-card-text>
              <v-switch
                v-model="state.auto"
                :label="$t('search.auto-search')"
                single-line
                color="primary"
              />
              <v-btn
                block
                color="primary"
                @click="reset"
              >
                {{ $t("general.reset") }}
              </v-btn>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
      <div
        v-if="!state.auto"
        class="search-button-container"
      >
        <v-btn
          size="large"
          color="primary"
          type="submit"
          rounded="pill"
          block
          flat
        >
          <v-icon start>
            {{ $globals.icons.search }}
          </v-icon>
          {{ $t("search.search") }}
        </v-btn>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import RecipeExplorerPageSearchFilters from "./RecipeExplorerPageSearchFilters.vue";
import { useRecipeExplorerSearch, clearRecipeExplorerSearchState } from "~/composables/use-recipe-explorer-search";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useCategoryStore, useHouseholdStore, usePublicCategoryStore, usePublicHouseholdStore } from "~/composables/store";
import type { RecipeCategory } from "~/lib/api/types/recipe";

const emit = defineEmits<{
  ready: [];
}>();

const auth = useMealieAuth();
const route = useRoute();
const { $globals } = useNuxtApp();
const i18n = useI18n();
const showRandomLoading = ref(false);

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const {
  state,
  selectedCategories,
  selectedFoods,
  selectedHouseholds,
  selectedTags,
  selectedTools,
  passedQueryWithSeed,
  search,
  reset,
  toggleOrderDirection,
  setOrderBy,
  setRandomOrderBy,
  filterItems,
  initialize,
} = useRecipeExplorerSearch(groupSlug);

const { isOwnGroup } = useLoggedInState();
const categoryStore = isOwnGroup.value ? useCategoryStore() : usePublicCategoryStore(groupSlug.value);

/** the most used categories, offered as one-tap filters */
const QUICK_CATEGORY_LIMIT = 4;
const quickCategories = computed(() => {
  const selected = selectedCategories.value;
  const rest = [...categoryStore.store.value]
    .filter(category => category.id && !selected.some(s => s.id === category.id))
    .sort((a, b) => (b.recipeCount ?? 0) - (a.recipeCount ?? 0) || a.name.localeCompare(b.name));
  // keep a selected category visible even when it would sort past the limit
  return [...selected, ...rest].slice(0, Math.max(QUICK_CATEGORY_LIMIT, selected.length));
});

const householdStore = isOwnGroup.value ? useHouseholdStore() : usePublicHouseholdStore(groupSlug.value);
const householdCount = computed(() => householdStore.store.value.length);

const hasActiveFilters = computed(() =>
  !!state.value.search
  || selectedCategories.value.length > 0
  || selectedFoods.value.length > 0
  || selectedTags.value.length > 0
  || selectedTools.value.length > 0
  || (selectedHouseholds.value.length > 0 && selectedHouseholds.value.length < householdCount.value),
);

const favoritesLink = computed(() => isOwnGroup.value && auth.user.value ? `/user/${auth.user.value.id}/favorites` : "");

function isOnlyCategory(id?: string | null) {
  return selectedCategories.value.length === 1 && selectedCategories.value[0]!.id === id;
}

function toggleCategory(category: RecipeCategory) {
  if (isOnlyCategory(category.id)) {
    selectedCategories.value = [];
    return;
  }
  filterItems(category, "categories");
}

defineExpose({
  passedQueryWithSeed,
  filterItems,
  hasActiveFilters,
});

onMounted(async () => {
  await initialize();
  emit("ready");
});

onUnmounted(() => {
  // Clear the cache when component unmounts to ensure fresh state on remount
  clearRecipeExplorerSearchState(groupSlug.value);
});

const sortText = computed(() => {
  const sort = sortable.value.find(s => s.value === state.value.orderBy);
  if (!sort) return "";
  return `${sort.name}`;
});

const sortable = computed(() => [
  {
    icon: $globals.icons.orderAlphabeticalAscending,
    name: i18n.t("general.sort-alphabetically"),
    value: "name",
  },
  {
    icon: $globals.icons.newBox,
    name: i18n.t("general.created"),
    value: "created_at",
  },
  {
    icon: $globals.icons.chefHat,
    name: i18n.t("general.last-made"),
    value: "last_made",
  },
  {
    icon: $globals.icons.star,
    name: i18n.t("general.rating"),
    value: "rating",
  },
  {
    icon: $globals.icons.update,
    name: i18n.t("general.updated"),
    value: "updated_at",
  },
  {
    icon: $globals.icons.diceMultiple,
    name: i18n.t("general.random"),
    value: "random",
  },
]);

// function to show refresh icon
async function setRandomOrderByWrapper() {
  if (!showRandomLoading.value) {
    showRandomLoading.value = true;
  }
  await setRandomOrderBy();
}
</script>

<style scoped>
.search-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.search-row__spacer {
  flex: 1;
}

.search-box {
  width: 100%;
}

.search-button-container {
  margin: 1.5rem auto 0 auto;
  max-width: 500px;
}
</style>
