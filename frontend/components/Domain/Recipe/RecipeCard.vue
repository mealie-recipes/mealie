<template>
  <v-hover v-slot="{ hover }" :open-delay="50">
    <v-card
      :class="{ 'on-hover': hover }"
      :elevation="hover ? 12 : 2"
      :to="route ? `/recipe/${slug}` : ''"
      min-height="275"
      @click="$emit('click')"
    >
      <RecipeCardImage icon-size="200" :slug="slug" small :image-version="image">
        <v-expand-transition v-if="description">
          <div v-if="hover" class="d-flex transition-fast-in-fast-out secondary v-card--reveal" style="height: 100%">
            <v-card-text class="v-card--text-show white--text">
              {{ description | truncate(300) }}
            </v-card-text>
          </div>
        </v-expand-transition>
      </RecipeCardImage>
      <v-card-title class="my-n3 mb-n6">
        <div class="headerClass">
          {{ name }}
        </div>
      </v-card-title>

      <v-card-actions>
        <RecipeFavoriteBadge v-if="loggedIn" :slug="slug" show-always />
        <RecipeRating :value="rating" :name="name" :slug="slug" :small="true" />
        <v-spacer></v-spacer>
        <RecipeChips :truncate="true" :items="tags" :title="false" :limit="2" :small="true" :is-category="false" />
        <RecipeContextMenu :slug="slug" :name="name" />
      </v-card-actions>
    </v-card>
  </v-hover>
</template>

<script>
import { api } from "@/api";
import RecipeFavoriteBadge from "./RecipeFavoriteBadge";
import RecipeChips from "./RecipeChips";
import RecipeContextMenu from "./RecipeContextMenu";
import RecipeCardImage from "./RecipeCardImage";
import RecipeRating from "./RecipeRating";
export default {
  components: { RecipeFavoriteBadge, RecipeChips, RecipeContextMenu, RecipeRating, RecipeCardImage },
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
      default: null,
    },
    rating: {
      type: Number,
      default: 0,
    },
    image: {
      type: String,
      default: null,
    },
    route: {
      type: Boolean,
      default: true,
    },
    tags: {
      type: Array,
      default: () => [],
    },
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
      return api.recipes.recipeSmallImage(slug, this.image);
    },
  },
};
</script>

<style>
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
</style>
