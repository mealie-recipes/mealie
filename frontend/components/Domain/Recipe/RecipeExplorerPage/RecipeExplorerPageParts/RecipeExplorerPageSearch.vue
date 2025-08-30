<template>
  <div class="search-container pb-8">
    <form
      class="search-box pa-2"
      @submit.prevent="handleSearch"
    >
      <div class="d-flex justify-center mb-2">
        <v-text-field
          ref="input"
          v-model="searchText"
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
        <RecipeExplorerPageSearchFilters
          v-model:require-all-categories="requireAllCategories"
          v-model:require-all-tags="requireAllTags"
          v-model:require-all-tools="requireAllTools"
          v-model:require-all-foods="requireAllFoods"
          v-model:selected-categories="selectedCategories"
          v-model:selected-tags="selectedTags"
          v-model:selected-tools="selectedTools"
          v-model:selected-foods="selectedFoods"
          v-model:selected-households="selectedHouseholds"
        />
        <!-- Sort Options -->
        <v-menu
          offset-y
          nudge-bottom="3"
        >
          <template #activator="{ props }">
            <v-btn
              class="ml-auto"
              size="small"
              color="accent"
              v-bind="props"
            >
              <v-icon :start="!$vuetify.display.xs">
                {{ orderDirection === "asc" ? $globals.icons.sortAscending : $globals.icons.sortDescending }}
              </v-icon>
              {{ $vuetify.display.xs ? null : sortText }}
            </v-btn>
          </template>
          <v-card>
            <v-list>
              <v-list-item
                slim
                density="comfortable"
                :prepend-icon="orderDirection === 'asc' ? $globals.icons.sortDescending : $globals.icons.sortAscending"
                :title="orderDirection === 'asc' ? $t('general.sort-descending') : $t('general.sort-ascending')"
                @click="$emit('toggle-order-direction')"
              />
              <v-divider />
              <v-list-item
                v-for="v in sortable"
                :key="v.name"
                :active="orderBy === v.value"
                slim
                density="comfortable"
                :prepend-icon="v.icon"
                :title="v.name"
                @click="$emit('set-order-by', v.value)"
              />
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
              color="accent"
              dark
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
                v-model="autoSearch"
                :label="$t('search.auto-search')"
                single-line
              />
              <v-btn
                block
                color="primary"
                @click="$emit('reset')"
              >
                {{ $t("general.reset") }}
              </v-btn>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
      <div
        v-if="!autoSearch"
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
import type { IngredientFood, RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { HouseholdSummary } from "~/lib/api/types/household";
import RecipeExplorerPageSearchFilters from "./RecipeExplorerPageSearchFilters.vue";

interface Props {
  search: string;
  orderBy: string;
  orderDirection: "asc" | "desc";
  auto: boolean;
  requireAllCategories: boolean;
  requireAllTags: boolean;
  requireAllTools: boolean;
  requireAllFoods: boolean;
  selectedCategories: NoUndefinedField<RecipeCategory>[];
  selectedTags: NoUndefinedField<RecipeTag>[];
  selectedTools: NoUndefinedField<RecipeTool>[];
  selectedFoods: IngredientFood[];
  selectedHouseholds: NoUndefinedField<HouseholdSummary>[];
}

const props = withDefaults(defineProps<Props>(), {
  search: "",
  orderBy: "created_at",
  orderDirection: "desc",
  auto: true,
  requireAllCategories: false,
  requireAllTags: false,
  requireAllTools: false,
  requireAllFoods: false,
  selectedCategories: () => [],
  selectedTags: () => [],
  selectedTools: () => [],
  selectedFoods: () => [],
  selectedHouseholds: () => [],
});

const emit = defineEmits<{
  'update:search': [value: string];
  'update:orderBy': [value: string];
  'update:orderDirection': [value: "asc" | "desc"];
  'update:auto': [value: boolean];
  'update:requireAllCategories': [value: boolean];
  'update:requireAllTags': [value: boolean];
  'update:requireAllTools': [value: boolean];
  'update:requireAllFoods': [value: boolean];
  'update:selectedCategories': [value: NoUndefinedField<RecipeCategory>[]];
  'update:selectedTags': [value: NoUndefinedField<RecipeTag>[]];
  'update:selectedTools': [value: NoUndefinedField<RecipeTool>[]];
  'update:selectedFoods': [value: IngredientFood[]];
  'update:selectedHouseholds': [value: NoUndefinedField<HouseholdSummary>[]];
  'search': [];
  'reset': [];
  'toggle-order-direction': [];
  'set-order-by': [value: string];
}>();

const { $globals } = useNuxtApp();
const i18n = useI18n();

// Two-way binding computed properties
const searchText = computed({
  get: () => props.search,
  set: (value) => emit('update:search', value)
});

const orderBy = computed({
  get: () => props.orderBy,
  set: (value) => emit('update:orderBy', value)
});

const orderDirection = computed({
  get: () => props.orderDirection,
  set: (value) => emit('update:orderDirection', value)
});

const autoSearch = computed({
  get: () => props.auto,
  set: (value) => emit('update:auto', value)
});

const requireAllCategories = computed({
  get: () => props.requireAllCategories,
  set: (value) => emit('update:requireAllCategories', value)
});

const requireAllTags = computed({
  get: () => props.requireAllTags,
  set: (value) => emit('update:requireAllTags', value)
});

const requireAllTools = computed({
  get: () => props.requireAllTools,
  set: (value) => emit('update:requireAllTools', value)
});

const requireAllFoods = computed({
  get: () => props.requireAllFoods,
  set: (value) => emit('update:requireAllFoods', value)
});

const selectedCategories = computed({
  get: () => props.selectedCategories,
  set: (value) => emit('update:selectedCategories', value)
});

const selectedTags = computed({
  get: () => props.selectedTags,
  set: (value) => emit('update:selectedTags', value)
});

const selectedTools = computed({
  get: () => props.selectedTools,
  set: (value) => emit('update:selectedTools', value)
});

const selectedFoods = computed({
  get: () => props.selectedFoods,
  set: (value) => emit('update:selectedFoods', value)
});

const selectedHouseholds = computed({
  get: () => props.selectedHouseholds,
  set: (value) => emit('update:selectedHouseholds', value)
});

// Computed properties
const sortText = computed(() => {
  const sort = sortable.value.find(s => s.value === props.orderBy);
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

// Methods
const input: Ref<any> = ref(null);

function hideKeyboard() {
  input.value?.blur();
}

function handleSearch() {
  emit('search');
}
</script>

<style scoped>
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
