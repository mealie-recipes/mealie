<template>
  <div>
    <slot v-bind="{ open, close }" />
    <v-dialog
      v-model="dialog"
      max-width="988px"
      content-class="top-dialog"
      :scrollable="false"
    >
      <v-card
        :rounded="!$vuetify.display.xs"
        :loading="loading"
      >
        <v-toolbar
          dark
          color="primary-lighten-1"
        >
          <v-text-field
            id="arrow-search"
            v-model="search.query.value"
            autofocus
            variant="solo"
            flat
            autocomplete="off"
            bg-color="primary-lighten-1"
            color="white"
            density="compact"
            class="mx-2 arrow-search"
            hide-details
            single-line
            :placeholder="$t('search.search')"
            :prepend-inner-icon="$globals.icons.search"
          />

          <v-btn
            v-if="$vuetify.display.xs"
            icon
            size="x-small"
            @click="dialog = false"
          >
            <v-icon>
              {{ $globals.icons.close }}
            </v-icon>
          </v-btn>
        </v-toolbar>

        <v-card-actions>
          <div class="mr-auto">
            {{ $t("search.results") }}
          </div>
        </v-card-actions>

        <div class="scroll pa-1" style="max-height: 700px;">
          <RecipeCardMobile
            v-for="(recipe, index) in search.data.value"
            :key="index"
            class="ma-1 arrow-nav"
            :class="{ 'keyboard-selected': index === selectedIndex }"
            :name="recipe.name ?? ''"
            :description="recipe.description ?? ''"
            :slug="recipe.slug ?? ''"
            :rating="recipe.rating ?? 0"
            :image="recipe.image"
            :recipe-id="recipe.id ?? ''"
            v-bind="$attrs.selected ? { selected: () => handleSelect(recipe) } : {}"
          />
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { RecipeSummary } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";
import { usePublicExploreApi } from "~/composables/api/api-client";

const SELECTED_EVENT = "selected";

// Define emits
const emit = defineEmits<{
  selected: [recipe: RecipeSummary];
}>();

const auth = useMealieAuth();
const loading = ref(false);
const selectedIndex = ref(-1);
const router = useRouter();
const attrs = useAttrs();

// ===========================================================================
// Dialog State Management
const dialog = ref(false);

// Reset or Grab Recipes on Change
watch(dialog, (val) => {
  if (!val) {
    search.query.value = "";
    selectedIndex.value = -1;
    search.data.value = [];
  }
});

// ===========================================================================
// Event Handlers

function scrollSelectedRecipeIntoView() {
  const recipeCards = document.getElementsByClassName("arrow-nav");

  if (!recipeCards.length || selectedIndex.value < 0 || selectedIndex.value >= recipeCards.length) {
    return;
  }

  recipeCards[selectedIndex.value]?.scrollIntoView({ block: "center" });
}

function activateRecipe(recipe: RecipeSummary | undefined) {
  if (!recipe) {
    return;
  }

  if (attrs.selected) {
    handleSelect(recipe);
    return;
  }

  if (!recipe.slug) {
    return;
  }

  close();
  router.push(`/g/${groupSlug.value}/r/${recipe.slug}`);
}

async function selectRecipe(positionChange: number) {
  selectedIndex.value += positionChange;
  selectedIndex.value = Math.max(selectedIndex.value, -1);
  selectedIndex.value = Math.min(selectedIndex.value, search.data.value.length - 1);
  await nextTick();
  scrollSelectedRecipeIntoView();
}

function onSearchKeydown(e: KeyboardEvent) {
  if (e.isComposing) {
    return;
  }

  if (e.key === "Enter") {
    e.preventDefault();
    const index = Math.max(selectedIndex.value, 0);
    activateRecipe(search.data.value[index]);
  }
  else if (e.key === "ArrowUp") {
    e.preventDefault();
    void selectRecipe(-1);
  }
  else if (e.key === "ArrowDown") {
    e.preventDefault();
    void selectRecipe(1);
  }
  else {
    return;
  }
}

watch(dialog, (val) => {
  if (!val) {
    document.removeEventListener("keydown", onSearchKeydown);
  }
  else {
    document.addEventListener("keydown", onSearchKeydown);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", onSearchKeydown);
});

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
watch(route, close);

function open() {
  dialog.value = true;
}
function close() {
  dialog.value = false;
}

// ===========================================================================
// Basic Search
const { isOwnGroup } = useLoggedInState();
const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;
const search = useRecipeSearch(api);

watch(() => search.data.value, () => {
  selectedIndex.value = -1;
});

// Select Handler
function handleSelect(recipe: RecipeSummary) {
  close();
  emit(SELECTED_EVENT, recipe);
}

// Expose functions to parent components
defineExpose({
  open,
  close,
});
</script>

<style scoped>
.scroll {
  overflow-y: auto;
}

.keyboard-selected {
  outline: 2px solid rgb(var(--v-theme-primary));
  border-radius: 4px;
}
</style>
