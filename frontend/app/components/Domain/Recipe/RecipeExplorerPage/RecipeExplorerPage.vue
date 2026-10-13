<template>
  <div class="library">
    <RecipeExplorerPageHeader />
    <RecipeExplorerPageSearch
      ref="searchComponent"
      class="library__filters"
      @ready="onSearchReady"
    />

    <!-- The overview steps aside while searching or filtering, so results come straight up -->
    <template v-if="showOverview">
      <RecipeExplorerPageTonight v-if="isOwnGroup" class="library__tonight" />
      <RecipeExplorerPageRecent class="library__recent" @see-all="scrollToAll" />
    </template>

    <div ref="allRecipes" class="library__all">
      <RecipeCardSection
        v-if="ready"
        hide-icon
        :title="showOverview ? $t('recipe-library.all-recipes') : $t('search.results')"
        :recipes="recipes"
        :query="searchQuery"
        disable-sort
        @item-selected="onItemSelected"
        @replace-recipes="replaceRecipes"
        @append-recipes="appendRecipes"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import RecipeExplorerPageHeader from "./RecipeExplorerPageParts/RecipeExplorerPageHeader.vue";
import RecipeExplorerPageRecent from "./RecipeExplorerPageParts/RecipeExplorerPageRecent.vue";
import RecipeExplorerPageSearch from "./RecipeExplorerPageParts/RecipeExplorerPageSearch.vue";
import RecipeExplorerPageTonight from "./RecipeExplorerPageParts/RecipeExplorerPageTonight.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLazyRecipes } from "~/composables/recipes";

const auth = useMealieAuth();
const route = useRoute();

const { isOwnGroup } = useLoggedInState();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const { recipes, appendRecipes, replaceRecipes } = useLazyRecipes(isOwnGroup.value ? null : groupSlug.value);

const ready = ref(false);
const searchComponent = ref<InstanceType<typeof RecipeExplorerPageSearch>>();
const allRecipes = ref<HTMLElement | null>(null);

const searchQuery = computed(() => {
  return searchComponent.value?.passedQueryWithSeed || {};
});

const showOverview = computed(() => ready.value && !searchComponent.value?.hasActiveFilters);

function onSearchReady() {
  ready.value = true;
}

function onItemSelected(item: any, urlPrefix: string) {
  searchComponent.value?.filterItems(item, urlPrefix);
}

function scrollToAll() {
  allRecipes.value?.scrollIntoView({ behavior: "smooth", block: "start" });
}
</script>

<style scoped>
.library {
  max-width: 1360px;
  margin: 0 auto;
  padding: 36px 48px 96px;
  box-sizing: border-box;
}

.library__filters {
  margin-top: 22px;
}

.library__tonight {
  margin-top: 24px;
}

.library__recent {
  margin-top: 32px;
}

.library__all {
  margin-top: 40px;
  scroll-margin-top: 72px;
}

@media (max-width: 960px) {
  .library {
    padding: 24px 24px 80px;
  }
}

@media (max-width: 600px) {
  .library {
    padding: 16px 16px 72px;
  }
}
</style>
