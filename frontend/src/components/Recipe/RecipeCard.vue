<template>
  <v-hover v-slot="{ hover }" :open-delay="50">
    <v-card
      :class="{ 'on-hover': hover }"
      :elevation="hover ? 12 : 2"
      :to="route ? `/recipe/${slug}` : ''"
      @click="$emit('click')"
      min-height="275"
    >
      <v-img height="200" :src="getImage(slug)">
        <v-expand-transition v-if="description">
          <div v-if="hover" class="d-flex transition-fast-in-fast-out secondary v-card--reveal  " style="height: 100%;">
            <v-card-text class="v-card--text-show white--text">
              {{ description | truncate(300) }}
            </v-card-text>
          </div>
        </v-expand-transition>
      </v-img>
      <v-card-title class="my-n3 mb-n6 ">
        <div class="headerClass">
          {{ name }}
        </div>
      </v-card-title>

      <v-card-actions>
        <Rating :value="rating" :name="name" :slug="slug" :small="true" />
        <v-spacer></v-spacer>
        <RecipeChips :truncate="true" :items="tags" :title="false" :limit="2" :small="true" :isCategory="false" />
        <ContextMenu :slug="slug" />
      </v-card-actions>
    </v-card>
  </v-hover>
</template>

<script>
import RecipeChips from "@/components/Recipe/RecipeViewer/RecipeChips";
import ContextMenu from "@/components/Recipe/ContextMenu";
import Rating from "@/components/Recipe/Parts/Rating";
import { api } from "@/api";
export default {
  components: {
    RecipeChips,
    ContextMenu,
    Rating,
  },
  props: {
    name: String,
    slug: String,
    description: String,
    rating: Number,
    image: String,

    route: {
      default: true,
    },
    tags: {
      default: true,
    },
  },
  methods: {
    getImage(image) {
      return api.recipes.recipeSmallImage(image);
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
