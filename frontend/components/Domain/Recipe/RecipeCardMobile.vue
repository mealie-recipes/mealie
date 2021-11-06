<template>
  <v-lazy>
    <v-expand-transition>
      <v-card
        :ripple="false"
        class="mx-auto"
        hover
        :to="$listeners.selected ? undefined : `/recipe/${slug}`"
        @click="$emit('selected')"
      >
        <v-list-item three-line>
          <slot name="avatar">
            <v-list-item-avatar tile size="125" class="v-mobile-img rounded-sm my-0 ml-n4">
              <v-img
                v-if="!fallBackImage"
                :src="getImage(slug)"
                @load="fallBackImage = false"
                @error="fallBackImage = true"
              ></v-img>
              <v-icon v-else color="primary" class="icon-position" size="100">
                {{ $globals.icons.primary }}
              </v-icon>
            </v-list-item-avatar>
          </slot>
          <v-list-item-content>
            <v-list-item-title class="mb-1">{{ name }} </v-list-item-title>
            <v-list-item-subtitle> {{ description }} </v-list-item-subtitle>
            <div class="d-flex justify-center align-center">
              <slot name="actions">
                <RecipeFavoriteBadge v-if="loggedIn" :slug="slug" show-always />
                <v-rating
                  color="secondary"
                  class="ml-auto"
                  background-color="secondary lighten-3"
                  dense
                  length="5"
                  size="15"
                  :value="rating"
                ></v-rating>
                <v-spacer></v-spacer>
                <RecipeContextMenu
                  :slug="slug"
                  :menu-icon="$globals.icons.dotsHorizontal"
                  :name="name"
                  :recipe-id="recipeId"
                  :use-items="{
                    delete: true,
                    edit: true,
                    download: true,
                    mealplanner: true,
                    print: false,
                    share: true,
                  }"
                  @deleted="$emit('delete', slug)"
                />
              </slot>
            </div>
          </v-list-item-content>
        </v-list-item>
        <slot />
      </v-card>
    </v-expand-transition>
  </v-lazy>
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge";
import RecipeContextMenu from "./RecipeContextMenu";
import { useApiSingleton } from "~/composables/use-api";
export default defineComponent({
  components: {
    RecipeFavoriteBadge,
    RecipeContextMenu,
  },
  props: {
    name: {
      type: String,
      required: true,
    },
    slug: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    rating: {
      type: Number,
      default: 0,
    },
    image: {
      type: [String, null],
      default: "",
    },
    route: {
      type: Boolean,
      default: true,
    },
    recipeId: {
      type: Number,
      required: true,
    },
  },
  setup() {
    const api = useApiSingleton();

    return { api };
  },
  data() {
    return {
      fallBackImage: false,
    };
  },
  computed: {
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
  },
  methods: {
    getImage(slug) {
      return this.api.recipes.recipeSmallImage(slug, this.image);
    },
  },
});
</script>

<style>
.v-mobile-img {
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 0;
}
.v-card--reveal {
  align-items: center;
  bottom: 0;
  justify-content: center;
  opacity: 0.8;
  position: absolute;
  width: 100%;
}
.v-card--text-show {
  opacity: 1 !important;
}
.headerClass {
  white-space: nowrap;
  word-break: normal;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-top {
  align-self: start !important;
}
</style>
