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
          <v-list-item @click="sortRecipes(EVENTS.lastMade)">
            <v-icon left>
              {{ $globals.icons.chefHat }}
            </v-icon>
            <v-list-item-title>{{ $t("general.last-made") }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <ContextMenu
        v-if="!$vuetify.breakpoint.smAndDown"
        :items="[
          {
            title: $tc('general.toggle-view'),
            icon: $globals.icons.eye,
            event: 'toggle-dense-view',
          },
        ]"
        @toggle-dense-view="toggleMobileCards()"
      />
    </v-app-bar>
    <div v-if="recipes && ready">
      <div class="mt-2">
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

                 v-on="$listeners"
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

                v-on="$listeners"
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
  useRoute,
  useRouter,
  watch,
} from "@nuxtjs/composition-api";
import { useThrottleFn } from "@vueuse/core";
import RecipeCard from "./RecipeCard.vue";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useAsyncKey } from "~/composables/use-utils";
import { useLazyRecipes } from "~/composables/recipes";
import { Recipe } from "~/lib/api/types/recipe";
import { useUserSortPreferences } from "~/composables/use-users/preferences";
import { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";

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
    query: {
      type: Object as () => RecipeSearchQuery,
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
      lastMade: "lastMade",
      shuffle: "shuffle",
    };

    const { $auth, $globals, $vuetify } = useContext();
    const { isOwnGroup } = useLoggedInState();
    const useMobileCards = computed(() => {
      return $vuetify.breakpoint.smAndDown || preferences.value.useMobileCards;
    });

    const displayTitleIcon = computed(() => {
      return props.icon || $globals.icons.tags;
    });

    const state = reactive({
      sortLoading: false,
    });

    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const page = ref(1);
    const perPage = 32;
    const hasMore = ref(true);
    const ready = ref(false);
    const loading = ref(false);

    const { fetchMore, getRandom } = useLazyRecipes(isOwnGroup.value ? null : groupSlug.value);
    const router = useRouter();

    const queryFilter = computed(() => {
      const orderBy = props.query?.orderBy || preferences.value.orderBy;
      const orderByFilter = preferences.value.filterNull && orderBy ? `${orderBy} IS NOT NULL` : null;

      if (props.query.queryFilter && orderByFilter) {
        return `(${props.query.queryFilter}) AND ${orderByFilter}`;
      } else if (props.query.queryFilter) {
        return props.query.queryFilter;
      } else {
        return orderByFilter;
      }
    });

    async function fetchRecipes(pageCount = 1) {
      return await fetchMore(
        page.value,
        perPage * pageCount,
        props.query?.orderBy || preferences.value.orderBy,
        props.query?.orderDirection || preferences.value.orderDirection,
        props.query,
        // we use a computed queryFilter to filter out recipes that have a null value for the property we're sorting by
        queryFilter.value
      );
    }

    onMounted(async () => {
      await initRecipes();
      ready.value = true;
    });

    let lastQuery: string | undefined = JSON.stringify(props.query);
    watch(
      () => props.query,
      async (newValue: RecipeSearchQuery | undefined) => {
        const newValueString = JSON.stringify(newValue)
        if (lastQuery !== newValueString) {
          lastQuery = newValueString;
          ready.value = false;
          await initRecipes();
          ready.value = true;
        }
      }
    );

    async function initRecipes() {
      page.value = 1;
      hasMore.value = true;

      // we double-up the first call to avoid a bug with large screens that render
      // the entire first page without scrolling, preventing additional loading
      const newRecipes = await fetchRecipes(page.value + 1);
      if (newRecipes.length < perPage) {
        hasMore.value = false;
      }

      // since we doubled the first call, we also need to advance the page
      page.value = page.value + 1;

      context.emit(REPLACE_RECIPES_EVENT, newRecipes);
    }

    const infiniteScroll = useThrottleFn(() => {
      useAsync(async () => {
        if (!hasMore.value || loading.value) {
          return;
        }

        loading.value = true;
        page.value = page.value + 1;

        const newRecipes = await fetchRecipes();
        if (newRecipes.length < perPage) {
          hasMore.value = false;
        }
        if (newRecipes.length) {
          context.emit(APPEND_RECIPES_EVENT, newRecipes);
        }

        loading.value = false;
      }, useAsyncKey());
    }, 500);


    function sortRecipes(sortType: string) {
      if (state.sortLoading || loading.value) {
        return;
      }

      function setter(
        orderBy: string,
        ascIcon: string,
        descIcon: string,
        defaultOrderDirection = "asc",
        filterNull = false
      ) {
        if (preferences.value.orderBy !== orderBy) {
          preferences.value.orderBy = orderBy;
          preferences.value.orderDirection = defaultOrderDirection;
          preferences.value.filterNull = filterNull;
        } else {
          preferences.value.orderDirection = preferences.value.orderDirection === "asc" ? "desc" : "asc";
        }
        preferences.value.sortIcon = preferences.value.orderDirection === "asc" ? ascIcon : descIcon;
      }

      switch (sortType) {
        case EVENTS.az:
          setter(
            "name",
            $globals.icons.sortAlphabeticalAscending,
            $globals.icons.sortAlphabeticalDescending,
            "asc",
            false
          );
          break;
        case EVENTS.rating:
          setter("rating", $globals.icons.sortAscending, $globals.icons.sortDescending, "desc", true);
          break;
        case EVENTS.created:
          setter(
            "created_at",
            $globals.icons.sortCalendarAscending,
            $globals.icons.sortCalendarDescending,
            "desc",
            false
          );
          break;
        case EVENTS.updated:
          setter("updated_at", $globals.icons.sortClockAscending, $globals.icons.sortClockDescending, "desc", false);
          break;
        case EVENTS.lastMade:
          setter(
            "last_made",
            $globals.icons.sortCalendarAscending,
            $globals.icons.sortCalendarDescending,
            "desc",
            true
          );
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
        const newRecipes = await fetchRecipes();
        context.emit(REPLACE_RECIPES_EVENT, newRecipes);

        state.sortLoading = false;
        loading.value = false;
      }, useAsyncKey());
    }

    async function navigateRandom() {
      const recipe = await getRandom(props.query, queryFilter.value);
      if (!recipe?.slug) {
        return;
      }

      router.push(`/g/${groupSlug.value}/r/${recipe.slug}`);
    }

    function toggleMobileCards() {
      preferences.value.useMobileCards = !preferences.value.useMobileCards;
    }

    return {
      ...toRefs(state),
      displayTitleIcon,
      EVENTS,
      infiniteScroll,
      ready,
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
