<template>
  <!-- Category Filter -->
  <SearchFilter
    v-if="categories"
    v-model="selectedCategories"
    v-model:require-all="state.requireAllCategories"
    :items="categories"
  >
    <v-icon start>
      {{ $globals.icons.categories }}
    </v-icon>
    {{ $t("category.categories") }}
  </SearchFilter>

  <!-- Tag Filter -->
  <SearchFilter
    v-if="tags"
    v-model="selectedTags"
    v-model:require-all="state.requireAllTags"
    :items="tags"
  >
    <v-icon start>
      {{ $globals.icons.tags }}
    </v-icon>
    {{ $t("tag.tags") }}
  </SearchFilter>

  <!-- Tool Filter -->
  <SearchFilter
    v-if="tools"
    v-model="selectedTools"
    v-model:require-all="state.requireAllTools"
    :items="tools"
  >
    <v-icon start>
      {{ $globals.icons.potSteam }}
    </v-icon>
    {{ $t("tool.tools") }}
  </SearchFilter>

  <!-- Food Filter -->
  <SearchFilter
    v-if="foods"
    v-model="selectedFoods"
    v-model:require-all="state.requireAllFoods"
    :items="foods"
  >
    <v-icon start>
      {{ $globals.icons.foods }}
    </v-icon>
    {{ $t("general.foods") }}
  </SearchFilter>

  <!-- Household Filter -->
  <SearchFilter
    v-if="households.length > 1"
    v-model="selectedHouseholds"
    :items="households"
    radio
  >
    <v-icon start>
      {{ $globals.icons.household }}
    </v-icon>
    {{ $t("household.households") }}
  </SearchFilter>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useRecipeExplorerSearch } from "~/composables/use-recipe-explorer-search";
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

const $auth = useMealieAuth();
const route = useRoute();

const { isOwnGroup } = useLoggedInState();
const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

const {
  state,
  selectedCategories,
  selectedFoods,
  selectedHouseholds,
  selectedTags,
  selectedTools,
} = useRecipeExplorerSearch(groupSlug);

const { store: categories } = isOwnGroup.value ? useCategoryStore() : usePublicCategoryStore(groupSlug.value);
const { store: tags } = isOwnGroup.value ? useTagStore() : usePublicTagStore(groupSlug.value);
const { store: tools } = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);
const { store: foods } = isOwnGroup.value ? useFoodStore() : usePublicFoodStore(groupSlug.value);
const { store: households } = isOwnGroup.value ? useHouseholdStore() : usePublicHouseholdStore(groupSlug.value);

watch(
  households,
  () => {
    // if exactly one household exists, then we shouldn't be filtering by household
    if (households.value.length == 1) {
      selectedHouseholds.value = [];
    }
  },
);
</script>
