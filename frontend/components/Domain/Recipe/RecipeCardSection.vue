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
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import RecipeCard from "./RecipeCard.vue";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useSorter } from "~/composables/recipes";
import {Recipe} from "~/types/api-types/recipe";

const SORT_EVENT = "sort";

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
    mobileCards: {
      type: Boolean,
      default: false,
    },
    singleColumn: {
      type: Boolean,
      default: false,
    },
    recipes: {
      type: Array as () => Recipe[],
      default: () => [],
    },
  },
  setup(props, context) {
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
      return props.mobileCards || $vuetify.breakpoint.smAndDown;
    });

    const displayTitleIcon = computed(() => {
      return props.icon || $globals.icons.tags;
    });

    const state = reactive({
      sortLoading: false,
    })

    const router = useRouter();
    function navigateRandom() {
      if (props.recipes.length > 0) {
        const recipe = props.recipes[Math.floor(Math.random() * props.recipes.length)];
        if (recipe.slug !== undefined) {
          router.push(`/recipe/${recipe.slug}`);
        }
      }
    }

    function sortRecipes(sortType: string) {
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
      ...toRefs(state),
      EVENTS,
      viewScale,
      displayTitleIcon,
      navigateRandom,
      sortRecipes,
    };
  },
});
</script>

<style>
.transparent {
  opacity: 1;
}
</style>
