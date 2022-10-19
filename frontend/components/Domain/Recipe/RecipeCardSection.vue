<template>
  <div>
    <v-app-bar v-if="!disableToolbar" color="transparent" flat class="mt-n1 flex-sm-wrap rounded">
      <slot name="title">
        <v-icon v-if="title" large left>
          {{ displayTitleIcon }}
        </v-icon>
        <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
      </slot>
      <v-spacer></v-spacer>
      <v-btn :icon="$vuetify.breakpoint.xsOnly" text :disabled="recipes.length === 0" @click="navigateRandom">
        <v-icon :left="!$vuetify.breakpoint.xsOnly">
          {{ $globals.icons.diceMultiple }}
        </v-icon>
        {{ $vuetify.breakpoint.xsOnly ? null : $t("general.random") }}
      </v-btn>

      <v-menu v-if="$listeners.sortRecipes" offset-y left>
        <template #activator="{ on, attrs }">
          <v-btn text :icon="$vuetify.breakpoint.xsOnly" v-bind="attrs" :loading="sortLoading" v-on="on">
            <v-icon :left="!$vuetify.breakpoint.xsOnly">
              {{ preferences.sortIcon }}
            </v-icon>
            {{ $vuetify.breakpoint.xsOnly ? null : $t("general.sort") }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="sortRecipes(EVENTS.az)">
            <v-icon left>
              {{ $globals.icons.orderAlphabeticalAscending }}
            </v-icon>
            <v-list-item-title>{{ $t("general.sort-alphabetically") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.rating)">
            <v-icon left>
              {{ $globals.icons.star }}
            </v-icon>
            <v-list-item-title>{{ $t("general.rating") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.created)">
            <v-icon left>
              {{ $globals.icons.newBox }}
            </v-icon>
            <v-list-item-title>{{ $t("general.created") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.updated)">
            <v-icon left>
              {{ $globals.icons.update }}
            </v-icon>
            <v-list-item-title>{{ $t("general.updated") }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <ContextMenu
        v-if="!$vuetify.breakpoint.xsOnly"
        :items="[
          {
            title: $t('general.toggle-view'),
            icon: $globals.icons.eye,
            event: 'toggle-dense-view',
          },
        ]"
        @toggle-dense-view="toggleMobileCards()"
      />
    </v-app-bar>
    <div v-if="recipes" class="mt-2">
      <v-row v-if="!useMobileCards">
        <v-col v-for="(recipe, index) in recipes" :key="recipe.slug + index" :sm="6" :md="6" :lg="4" :xl="3">
          <v-lazy>
            <RecipeCard
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
              :recipe-id="recipe.id"
              @delete="$emit('delete', recipe.slug)"
            />
          </v-lazy>
        </v-col>
      </v-row>
      <v-row v-else dense>
        <v-col
          v-for="recipe in recipes"
          :key="recipe.name"
          cols="12"
          :sm="singleColumn ? '12' : '12'"
          :md="singleColumn ? '12' : '6'"
          :lg="singleColumn ? '12' : '4'"
          :xl="singleColumn ? '12' : '3'"
        >
          <v-lazy>
            <RecipeCardMobile
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
              :recipe-id="recipe.id"
              @delete="$emit('delete', recipe.slug)"
            />
          </v-lazy>
        </v-col>
      </v-row>
    </div>
    <v-card v-intersect="infiniteScroll"></v-card>
    <v-fade-transition>
      <AppLoader v-if="loading" :loading="loading" />
    </v-fade-transition>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  ref,
  toRefs,
  useAsync,
  useContext,
  useRouter,
} from "@nuxtjs/composition-api";
import { useThrottleFn } from "@vueuse/core";
import RecipeCard from "./RecipeCard.vue";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useAsyncKey } from "~/composables/use-utils";
import { useLazyRecipes } from "~/composables/recipes";
import { Recipe } from "~/lib/api/types/recipe";
import { useUserSortPreferences } from "~/composables/use-users/preferences";

const REPLACE_RECIPES_EVENT = "replaceRecipes";
const APPEND_RECIPES_EVENT = "appendRecipes";

export default defineComponent({
  components: {
    RecipeCard,
    RecipeCardMobile,
  },
  props: {
    disableToolbar: {
      type: Boolean,
      default: false,
    },
    icon: {
      type: String,
      default: null,
    },
    title: {
      type: String,
      default: null,
    },
    singleColumn: {
      type: Boolean,
      default: false,
    },
    recipes: {
      type: Array as () => Recipe[],
      default: () => [],
    },
    cookbookSlug: {
      type: String,
      default: null,
    },
    categorySlug: {
      type: String,
      default: null,
    },
    tagSlug: {
      type: String,
      default: null,
    },
    toolSlug: {
      type: String,
      default: null,
    },
  },
  setup(props, context) {
    const preferences = useUserSortPreferences();

    const EVENTS = {
      az: "az",
      rating: "rating",
      created: "created",
      updated: "updated",
      shuffle: "shuffle",
    };

    const { $globals, $vuetify } = useContext();
    const useMobileCards = computed(() => {
      return $vuetify.breakpoint.smAndDown || preferences.value.useMobileCards;
    });

    const displayTitleIcon = computed(() => {
      return props.icon || $globals.icons.tags;
    });

    const state = reactive({
      sortLoading: false,
    });

    const router = useRouter();
    function navigateRandom() {
      if (props.recipes.length > 0) {
        const recipe = props.recipes[Math.floor(Math.random() * props.recipes.length)];
        if (recipe.slug !== undefined) {
          router.push(`/recipe/${recipe.slug}`);
        }
      }
    }

    const page = ref(1);
    const perPage = ref(32);
    const hasMore = ref(true);
    const ready = ref(false);
    const loading = ref(false);

    const cookbook = ref<string>(props.cookbookSlug);
    const category = ref<string>(props.categorySlug);
    const tag = ref<string>(props.tagSlug);
    const tool = ref<string>(props.toolSlug);

    const { fetchMore } = useLazyRecipes();

    onMounted(async () => {
      const newRecipes = await fetchMore(
        page.value,

        // we double-up the first call to avoid a bug with large screens that render the entire first page without scrolling, preventing additional loading
        perPage.value * 2,
        preferences.value.orderBy,
        preferences.value.orderDirection,
        cookbook.value,
        category.value,
        tag.value,
        tool.value
      );

      // since we doubled the first call, we also need to advance the page
      page.value = page.value + 1;

      context.emit(REPLACE_RECIPES_EVENT, newRecipes);
      ready.value = true;
    });

    const infiniteScroll = useThrottleFn(() => {
      useAsync(async () => {
        if (!ready.value || !hasMore.value || loading.value) {
          return;
        }

        loading.value = true;
        page.value = page.value + 1;

        const newRecipes = await fetchMore(
          page.value,
          perPage.value,
          preferences.value.orderBy,
          preferences.value.orderDirection,
          cookbook.value,
          category.value,
          tag.value,
          tool.value
        );
        if (!newRecipes.length) {
          hasMore.value = false;
        } else {
          context.emit(APPEND_RECIPES_EVENT, newRecipes);
        }

        loading.value = false;
      }, useAsyncKey());
    }, 500);

    function sortRecipes(sortType: string) {
      if (state.sortLoading || loading.value) {
        return;
      }

      function setter(orderBy: string, ascIcon: string, descIcon: string) {
        if (preferences.value.orderBy !== orderBy) {
          preferences.value.orderBy = orderBy;
          preferences.value.orderDirection = "asc";
        } else {
          preferences.value.orderDirection = preferences.value.orderDirection === "asc" ? "desc" : "asc";
        }
        preferences.value.sortIcon = preferences.value.orderDirection === "asc" ? ascIcon : descIcon;
      }

      switch (sortType) {
        case EVENTS.az:
          setter("name", $globals.icons.sortAlphabeticalAscending, $globals.icons.sortAlphabeticalDescending);
          break;
        case EVENTS.rating:
          setter("rating", $globals.icons.sortAscending, $globals.icons.sortDescending);
          break;
        case EVENTS.created:
          setter("created_at", $globals.icons.sortCalendarAscending, $globals.icons.sortCalendarDescending);
          break;
        case EVENTS.updated:
          setter("update_at", $globals.icons.sortClockAscending, $globals.icons.sortClockDescending);
          break;
        default:
          console.log("Unknown Event", sortType);
          return;
      }

      useAsync(async () => {
        // reset pagination
        page.value = 1;
        hasMore.value = true;

        state.sortLoading = true;
        loading.value = true;

        // fetch new recipes
        const newRecipes = await fetchMore(
          page.value,
          perPage.value,
          preferences.value.orderBy,
          preferences.value.orderDirection,
          cookbook.value,
          category.value,
          tag.value,
          tool.value
        );
        context.emit(REPLACE_RECIPES_EVENT, newRecipes);

        state.sortLoading = false;
        loading.value = false;
      }, useAsyncKey());
    }

    function toggleMobileCards() {
      preferences.value.useMobileCards = !preferences.value.useMobileCards;
    }

    return {
      ...toRefs(state),
      displayTitleIcon,
      EVENTS,
      infiniteScroll,
      loading,
      navigateRandom,
      preferences,
      sortRecipes,
      toggleMobileCards,
      useMobileCards,
    };
  },
});
</script>

<style>
.transparent {
  opacity: 1;
}
</style>
