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

const emit = defineEmits<{
  'search': [];
  'reset': [];
  'toggle-order-direction': [];
  'set-order-by': [value: string];
}>();

const { $globals } = useNuxtApp();
const i18n = useI18n();

const searchText = defineModel<string>('search', { default: '' });
const orderBy = defineModel<string>('orderBy', { default: 'created_at' });
const orderDirection = defineModel<"asc" | "desc">('orderDirection', { default: 'desc' });
const autoSearch = defineModel<boolean>('auto', { default: true });
const requireAllCategories = defineModel<boolean>('requireAllCategories', { default: false });
const requireAllTags = defineModel<boolean>('requireAllTags', { default: false });
const requireAllTools = defineModel<boolean>('requireAllTools', { default: false });
const requireAllFoods = defineModel<boolean>('requireAllFoods', { default: false });
const selectedCategories = defineModel<NoUndefinedField<RecipeCategory>[]>('selectedCategories', { default: () => [] });
const selectedTags = defineModel<NoUndefinedField<RecipeTag>[]>('selectedTags', { default: () => [] });
const selectedTools = defineModel<NoUndefinedField<RecipeTool>[]>('selectedTools', { default: () => [] });
const selectedFoods = defineModel<IngredientFood[]>('selectedFoods', { default: () => [] });
const selectedHouseholds = defineModel<NoUndefinedField<HouseholdSummary>[]>('selectedHouseholds', { default: () => [] });

const sortText = computed(() => {
  const sort = sortable.value.find(s => s.value === orderBy.value);
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
