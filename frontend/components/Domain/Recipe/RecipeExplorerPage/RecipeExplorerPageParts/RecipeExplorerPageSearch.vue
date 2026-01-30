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
                @click="v.value === 'random' ? setRandomOrderByWrapper() : setOrderBy(v.value)"
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
import RecipeExplorerPageSearchFilters from "./RecipeExplorerPageSearchFilters.vue";
import { useRecipeExplorerSearch, clearRecipeExplorerSearchState } from "~/composables/use-recipe-explorer-search";

const emit = defineEmits<{
  ready: [];
}>();

const $auth = useMealieAuth();
const route = useRoute();
const { $globals } = useNuxtApp();
const i18n = useI18n();
const showRandomLoading = ref(false);

const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

const {
  state,
  passedQueryWithSeed,
  search,
  reset,
  toggleOrderDirection,
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

// Methods
const input: Ref<any> = ref(null);

function hideKeyboard() {
  input.value?.blur();
}

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
