<template>
  <div>
    <!-- Section Toolbar -->
    <v-app-bar v-if="toolbar" color="transparent" flat class="mt-n1 flex-sm-wrap rounded">
      <slot name="title">
        <v-icon v-if="title" large left>
          {{ displayIcon }}
        </v-icon>
        <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
      </slot>
      <v-spacer></v-spacer>
      <v-btn :icon="$vuetify.breakpoint.xsOnly" text :disabled="recipes.length === 0">
        <v-icon :left="!$vuetify.breakpoint.xsOnly">
          {{ $globals.icons.diceMultiple }}
        </v-icon>
        {{ $vuetify.breakpoint.xsOnly ? null : $t("general.random") }}
      </v-btn>

      <v-menu v-if="$listeners.sortRecipes" offset-y left>
        <template #activator="{ on, attrs }">
          <v-btn text :icon="$vuetify.breakpoint.xsOnly" v-bind="attrs" v-on="on">
            <v-icon :left="!$vuetify.breakpoint.xsOnly">
              {{ $globals.icons.sort }}
            </v-icon>
            {{ $vuetify.breakpoint.xsOnly ? null : $t("general.sort") }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item v-for="sort in sorters" :key="sort.id" @click="sort.action">
            <v-icon left>
              {{ sort.icon }}
            </v-icon>
            <v-list-item-title>{{ sort.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <ContextMenu
        v-if="!$vuetify.breakpoint.xsOnly"
        :menu-top="false"
        :items="[
          {
            title: $tc('general.toggle-view'),
            icon: $globals.icons.eye,
            event: 'toggle-dense-view',
          },
        ]"
        @toggle-dense-view="() => (state.preferMobileCards = !state.preferMobileCards)"
      />
    </v-app-bar>

    <!-- Recipe Section -->
    <div v-if="recipes && recipes.length > 0" class="mt-2">
      <v-row v-if="!mobileCards">
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
            />
          </v-lazy>
        </v-col>
      </v-row>
      <v-row v-else dense>
        <v-col v-for="recipe in recipes" :key="recipe.name" cols="12" :sm="'12'" :md="'6'" :lg="'4'" :xl="'3'">
          <v-lazy>
            <RecipeCardMobile
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
              :recipe-id="recipe.id"
            />
          </v-lazy>
        </v-col>
      </v-row>
      <v-card v-intersect="infiniteScroll"></v-card>
    </div>
    <div v-else class="d-flex justify-center">
      <div class="text-center">
        <v-icon size="64">
          {{ $globals.icons.search }}
        </v-icon>
        <p class="headline">No Results</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import RecipeCard from "./RecipeCard.vue";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { Recipe } from "~/lib/api/types/recipe";

const EVENTS = {
  az: "az",
  rating: "rating",
  created: "created",
  updated: "updated",
  lastMade: "lastMade",
} as const;

export default defineComponent({
  components: {
    RecipeCard,
    RecipeCardMobile,
  },
  props: {
    toolbar: {
      type: Boolean,
      default: true,
    },
    icon: {
      type: String,
      default: null,
    },
    title: {
      type: String,
      default: null,
    },
    recipes: {
      type: Array as () => Recipe[],
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { emit }) {
    const { $globals, i18n, $vuetify } = useContext();

    const state = ref({
      preferMobileCards: false,
    });

    const displayIcon = computed(() => props.icon || $globals.icons.tags);
    const mobileCards = computed(() => $vuetify.breakpoint.xsOnly || state.value.preferMobileCards);

    const sorters = computed(() => {
      return [
        {
          id: 1,
          label: i18n.t("general.sort-alphabetically"),
          icon: $globals.icons.orderAlphabeticalAscending,
          action: () => emit(EVENTS.az),
        },
        {
          id: 2,
          label: i18n.t("general.rating"),
          icon: $globals.icons.star,
          action: () => emit(EVENTS.rating),
        },
        {
          id: 3,
          label: i18n.t("general.created"),
          icon: $globals.icons.newBox,
          action: () => emit(EVENTS.created),
        },
        {
          id: 4,
          label: i18n.t("general.updated"),
          icon: $globals.icons.update,
          action: () => emit(EVENTS.updated),
        },
        {
          id: 5,
          label: i18n.t("general.last-made"),
          icon: $globals.icons.chefHat,
          action: () => emit(EVENTS.lastMade),
        },
      ];
    });

    function infiniteScroll() {
      emit("intersect");
    }

    return {
      state,
      sorters,
      displayIcon,
      mobileCards,
      infiniteScroll,
    };
  },
});
</script>

<style scoped></style>
