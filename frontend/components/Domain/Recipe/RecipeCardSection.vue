<template>
  <div>
    <v-app-bar v-if="!disableToolbar" color="transparent" flat class="mt-n1 flex-sm-wrap rounded">
      <v-icon v-if="title" large left>
        {{ displayTitleIcon }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn :icon="$vuetify.breakpoint.xsOnly" text @click="navigateRandom">
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
          <v-list-item @click="sortRecipes(EVENTS.shuffle)">
            <v-icon left>
              {{ $globals.icons.shuffleVariant }}
            </v-icon>
            <v-list-item-title>{{ $t("general.shuffle") }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <div v-if="recipes" class="mt-2">
      <v-row v-if="!viewScale">
        <v-col v-for="recipe in recipes" :key="recipe.name" :sm="6" :md="6" :lg="4" :xl="3">
          <v-lazy>
            <RecipeCard
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
            />
          </v-lazy>
        </v-col>
      </v-row>
      <v-row v-else dense>
        <v-col
          v-for="recipe in recipes.slice(0, cardLimit)"
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
            />
          </v-lazy>
        </v-col>
      </v-row>
    </div>
    <div v-intersect="bumpList" class="d-flex mt-5">
      <v-fade-transition>
        <AppLoader v-if="loading" :loading="loading" />
      </v-fade-transition>
    </div>
  </div>
</template>

<script>
import RecipeCard from "./RecipeCard";
import RecipeCardMobile from "./RecipeCardMobile";
import { useSorter } from "~/composables/use-recipes";
const SORT_EVENT = "sort";

export default {
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
    hardLimit: {
      type: [String, Number],
      default: 99999,
    },
    mobileCards: {
      type: Boolean,
      default: false,
    },
    singleColumn: {
      type: Boolean,
      defualt: false,
    },
    recipes: {
      type: Array,
      default: () => [],
    },
  },
  setup() {
    const utils = useSorter();

    return { utils };
  },
  data() {
    return {
      sortLoading: false,
      cardLimit: 50,
      loading: false,
      EVENTS: {
        az: "az",
        rating: "rating",
        created: "created",
        updated: "updated",
        shuffle: "shuffle",
      },
    };
  },
  computed: {
    viewScale() {
      if (this.mobileCards) return true;
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
    effectiveHardLimit() {
      return Math.min(this.hardLimit, this.recipes.length);
    },
    displayTitleIcon() {
      return this.icon || this.$globals.icons.tags;
    },
  },
  watch: {
    recipes() {
      this.bumpList();
    },
  },
  methods: {
    bumpList() {
      const newCardLimit = Math.min(this.cardLimit + 20, this.effectiveHardLimit);

      if (this.loading === false && newCardLimit > this.cardLimit) {
        this.setLoader();
      }

      this.cardLimit = newCardLimit;
    },
    async setLoader() {
      this.loading = true;
      // eslint-disable-next-line promise/param-names
      await new Promise((r) => setTimeout(r, 1000));
      this.loading = false;
    },
    navigateRandom() {
      const recipe = this.utils.recipe.randomRecipe(this.recipes);
      this.$router.push(`/recipe/${recipe.slug}`);
    },
    sortRecipes(sortType) {
      this.sortLoading = true;
      const sortTarget = [...this.recipes];
      switch (sortType) {
        case this.EVENTS.az:
          this.utils.sortAToZ(sortTarget);
          break;
        case this.EVENTS.rating:
          this.utils.sortByRating(sortTarget);
          break;
        case this.EVENTS.created:
          this.utils.sortByCreated(sortTarget);
          break;
        case this.EVENTS.updated:
          this.utils.sortByUpdated(sortTarget);
          break;
        case this.EVENTS.shuffle:
          this.utils.shuffle(sortTarget);
          break;
        default:
          console.log("Unknown Event", sortType);
          return;
      }
      this.$emit(SORT_EVENT, sortTarget);
      this.sortLoading = false;
    },
  },
};
</script>

<style>
.transparent {
  opacity: 1;
}
</style>
