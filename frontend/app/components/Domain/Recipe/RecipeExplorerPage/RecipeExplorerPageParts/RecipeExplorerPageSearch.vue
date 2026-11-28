<template>
  <div class="search-container pb-8">
    <form
      class="search-box pa-2"
      @submit.prevent="search"
    >
      <div class="d-flex justify-center mb-2">
        <v-text-field
          ref="input"
          v-model="state.search"
          variant="outlined"
          hide-details
          clearable
          color="primary"
          :placeholder="$t('search.search-placeholder')"
          :prepend-inner-icon="$globals.icons.search"
          @keyup.enter="hideKeyboard"
        />
      </div>
      <div class="search-row">
        <RecipeExplorerPageSearchFilters />
        <v-btn
          v-if="isOwnGroup"
          size="small"
          :color="state.favoritesOnly ? 'primary' : 'accent'"
          :aria-pressed="state.favoritesOnly"
          @click="state.favoritesOnly = !state.favoritesOnly"
        >
          <v-icon start>
            {{ state.favoritesOnly ? $globals.icons.heart : $globals.icons.heartOutline }}
          </v-icon>
          {{ $t('search.favorites-only') }}
        </v-btn>
        <v-btn size="small" variant="text" @click="clearFilters">
          {{ $t('search.clear-filters') }}
        </v-btn>
        <div class="search-actions">
          <v-menu
            location="bottom end"
            :offset="8"
          >
            <template #activator="{ props }">
              <v-btn
                class="search-sort-button"
                size="small"
                color="accent"
                :aria-label="$t('search.sort-by', { sort: selectedSort?.name || '' })"
                v-bind="props"
              >
                <v-icon start>
                  {{ selectedSort?.icon || $globals.icons.sortAscending }}
                </v-icon>
                <span class="text-truncate">{{ selectedSort?.name }}</span>
              </v-btn>
            </template>
            <v-card>
              <v-list>
                <v-list-item
                  v-for="v in sortable"
                  :key="v.name"
                  :active="state.orderBy === v.value && (v.value === 'random' || state.orderDirection === v.direction)"
                  slim
                  density="comfortable"
                  @click.stop="selectSort(v.value, v.direction)"
                >
                  <template #prepend>
                    <v-icon>{{ v.icon }}</v-icon>
                  </template>

                  <template #title>
                    <span>{{ v.name }}</span>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
          <!-- Settings -->
          <v-menu
            location="bottom end"
            :offset="8"
            :close-on-content-click="false"
          >
            <template #activator="{ props }">
              <v-btn
                size="small"
                color="accent"
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
      </div>
      <div
        v-if="!state.auto"
        class="search-button-container"
      >
        <v-btn
          size="x-large"
          color="primary"
          type="submit"
          block
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
import {
  mdiSortAlphabeticalAscending,
  mdiSortAlphabeticalDescending,
  mdiSortCalendarAscending,
  mdiSortCalendarDescending,
  mdiSortClockAscending,
  mdiSortClockDescending,
  mdiSortNumericAscending,
  mdiSortNumericDescending,
} from "@mdi/js";
import { recipeSortOptions } from "~/composables/use-recipe-search-options";
import RecipeExplorerPageSearchFilters from "./RecipeExplorerPageSearchFilters.vue";
import { useRecipeExplorerSearch, clearRecipeExplorerSearchState } from "~/composables/use-recipe-explorer-search";

const emit = defineEmits<{
  ready: [];
}>();

const auth = useMealieAuth();
const { isOwnGroup } = useLoggedInState();
const route = useRoute();
const { $globals } = useNuxtApp();
const i18n = useI18n();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const {
  state,
  passedQueryWithSeed,
  search,
  reset,
  clearFilters,
  setOrderBy,
  setRandomOrderBy,
  filterItems,
  initialize,
} = useRecipeExplorerSearch(groupSlug);

defineExpose({
  passedQueryWithSeed,
  filterItems,
});

onMounted(async () => {
  await initialize();
  emit("ready");
});

onUnmounted(() => {
  // Clear the cache when component unmounts to ensure fresh state on remount
  clearRecipeExplorerSearchState(groupSlug.value);
});

const calendarSortIcons = { asc: mdiSortCalendarAscending, desc: mdiSortCalendarDescending };
const sortIcons = {
  name: { asc: mdiSortAlphabeticalAscending, desc: mdiSortAlphabeticalDescending },
  created_at: calendarSortIcons,
  rating: { asc: mdiSortNumericAscending, desc: mdiSortNumericDescending },
  total_time_seconds: { asc: mdiSortClockAscending, desc: mdiSortClockDescending },
  last_made: calendarSortIcons,
  updated_at: calendarSortIcons,
  random: { asc: $globals.icons.diceMultiple, desc: $globals.icons.diceMultiple },
};
const sortable = computed(() => recipeSortOptions
  .filter(([field]) => isOwnGroup.value || field !== "last_made")
  .map(([value, direction, label]) => ({ value, direction, name: i18n.t(`search.sort-options.${label}`), icon: sortIcons[value][direction] })));
const selectedSort = computed(() => sortable.value.find(option => option.value === state.value.orderBy && (option.value === "random" || option.direction === state.value.orderDirection)));
function selectSort(value: string, direction: "asc" | "desc") {
  state.value.orderDirection = direction;
  if (value === "random") setRandomOrderBy();
  else setOrderBy(value);
}

// Methods
const input: Ref<any> = ref(null);

function hideKeyboard() {
  input.value?.blur();
}
</script>

<style scoped>
.search-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-box {
  width: 950px;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-inline-start: auto;
  max-width: 100%;
}

.search-sort-button {
  min-width: 0;
  max-width: 11rem;
  flex-shrink: 1;
}

.search-sort-button :deep(.v-btn__content) {
  min-width: 0;
}

.search-button-container {
  margin: 3rem auto 0 auto;
  max-width: 500px;
}
</style>
