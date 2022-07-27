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

      <v-menu v-if="$listeners.sort" offset-y left>
        <template #activator="{ on, attrs }">
          <v-btn text :icon="$vuetify.breakpoint.xsOnly" v-bind="attrs" :loading="sortLoading" v-on="on">
            <v-icon :left="!$vuetify.breakpoint.xsOnly">
              {{ $globals.icons.sort }}
            </v-icon>
            {{ $vuetify.breakpoint.xsOnly ? null : $t("general.sort") }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="sortRecipesFrontend(EVENTS.az)">
            <v-icon left>
              {{ $globals.icons.orderAlphabeticalAscending }}
            </v-icon>
            <v-list-item-title>{{ $t("general.sort-alphabetically") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipesFrontend(EVENTS.rating)">
            <v-icon left>
              {{ $globals.icons.star }}
            </v-icon>
            <v-list-item-title>{{ $t("general.rating") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipesFrontend(EVENTS.created)">
            <v-icon left>
              {{ $globals.icons.newBox }}
            </v-icon>
            <v-list-item-title>{{ $t("general.created") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipesFrontend(EVENTS.updated)">
            <v-icon left>
              {{ $globals.icons.update }}
            </v-icon>
            <v-list-item-title>{{ $t("general.updated") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipesFrontend(EVENTS.shuffle)">
            <v-icon left>
              {{ $globals.icons.shuffleVariant }}
            </v-icon>
            <v-list-item-title>{{ $t("general.shuffle") }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <v-menu v-if="$listeners.sortRecipes" offset-y left>
        <template #activator="{ on, attrs }">
          <v-btn text :icon="$vuetify.breakpoint.xsOnly" v-bind="attrs" :loading="sortLoading" v-on="on">
            <v-icon :left="!$vuetify.breakpoint.xsOnly">
              {{ $globals.icons.sort }}
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
            title: 'Toggle View',
            icon: $globals.icons.eye,
            event: 'toggle-dense-view',
          },
        ]"
        @toggle-dense-view="mobileCards = !mobileCards"
      />
    </v-app-bar>
    <div v-if="recipes" class="mt-2">
      <v-row v-if="!viewScale">
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
    <div v-if="usePagination">
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
  useRouter,
} from "@nuxtjs/composition-api";
import { useThrottleFn } from "@vueuse/core";
import RecipeCard from "./RecipeCard.vue";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useAsyncKey } from "~/composables/use-utils";
import { useLazyRecipes, useSorter } from "~/composables/recipes";
import { Recipe } from "~/types/api-types/recipe";

const SORT_EVENT = "sort";
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
    usePagination: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    const mobileCards = ref(false);
    const utils = useSorter();

    const EVENTS = {
      az: "az",
      rating: "rating",
      created: "created",
      updated: "updated",
      shuffle: "shuffle",
    };

    const { $globals, $vuetify } = useContext();
    const viewScale = computed(() => {
      return mobileCards.value || $vuetify.breakpoint.smAndDown;
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
    const perPage = ref(30);
    const orderBy = ref("name");
    const orderDirection = ref("asc");
    const hasMore = ref(true);

    const ready = ref(false);
    const loading = ref(false);

    const { recipes, fetchMore } = useLazyRecipes();

    onMounted(async () => {
      if (props.usePagination) {
        const newRecipes = await fetchMore(page.value, perPage.value, orderBy.value, orderDirection.value);
        context.emit(REPLACE_RECIPES_EVENT, newRecipes);
        ready.value = true;
      }
    });

    const infiniteScroll = useThrottleFn(() => {
      useAsync(async () => {
        if (!ready.value || !hasMore.value || loading.value) {
          return;
        }

        loading.value = true;
        page.value = page.value + 1;

        const newRecipes = await fetchMore(page.value, perPage.value, orderBy.value, orderDirection.value);
        if (!newRecipes.length) {
          hasMore.value = false;
        } else {
          context.emit(APPEND_RECIPES_EVENT, newRecipes);
        }

        loading.value = false;
      }, useAsyncKey());
    }, 500);

    /*
    sortRecipes helps filter using the API. This will eventually replace the sortRecipesFrontend function which pulls all recipes
    (without pagination) and does the sorting in the frontend.

    TODO: remove sortRecipesFrontend and remove duplicate "sortRecipes" section in the template (above)
    TODO: use indicator to show asc / desc order
    */

    function sortRecipes(sortType: string) {
      if (state.sortLoading || loading.value) {
        return;
      }

      switch (sortType) {
        case EVENTS.az:
          if (orderBy.value !== "name") {
            orderBy.value = "name";
            orderDirection.value = "asc";
          } else {
            orderDirection.value = orderDirection.value === "asc" ? "desc" : "asc";
          }
          break;
        case EVENTS.rating:
          if (orderBy.value !== "rating") {
            orderBy.value = "rating";
            orderDirection.value = "desc";
          } else {
            orderDirection.value = orderDirection.value === "asc" ? "desc" : "asc";
          }
          break;
        case EVENTS.created:
          if (orderBy.value !== "created_at") {
            orderBy.value = "created_at";
            orderDirection.value = "desc";
          } else {
            orderDirection.value = orderDirection.value === "asc" ? "desc" : "asc";
          }
          break;
        case EVENTS.updated:
          if (orderBy.value !== "update_at") {
            orderBy.value = "update_at";
            orderDirection.value = "desc";
          } else {
            orderDirection.value = orderDirection.value === "asc" ? "desc" : "asc";
          }
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
        const newRecipes = await fetchMore(page.value, perPage.value, orderBy.value, orderDirection.value);
        context.emit(REPLACE_RECIPES_EVENT, newRecipes);

        state.sortLoading = false;
        loading.value = false;
      }, useAsyncKey());
    }

    function sortRecipesFrontend(sortType: string) {
      state.sortLoading = true;
      const sortTarget = [...props.recipes];
      switch (sortType) {
        case EVENTS.az:
          utils.sortAToZ(sortTarget);
          break;
        case EVENTS.rating:
          utils.sortByRating(sortTarget);
          break;
        case EVENTS.created:
          utils.sortByCreated(sortTarget);
          break;
        case EVENTS.updated:
          utils.sortByUpdated(sortTarget);
          break;
        case EVENTS.shuffle:
          utils.shuffle(sortTarget);
          break;
        default:
          console.log("Unknown Event", sortType);
          return;
      }
      context.emit(SORT_EVENT, sortTarget);
      state.sortLoading = false;
    }

    return {
      mobileCards,
      ...toRefs(state),
      EVENTS,
      viewScale,
      displayTitleIcon,
      infiniteScroll,
      loading,
      navigateRandom,
      sortRecipes,
      sortRecipesFrontend,
    };
  },
});
</script>

<style>
.transparent {
  opacity: 1;
}
</style>
