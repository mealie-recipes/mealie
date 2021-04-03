<template>
  <v-card
    hover
    :to="`/recipe/${slug}`"
    max-height="125"
    @click="$emit('selected')"
  >
    <v-list-item>
      <v-list-item-avatar rounded size="125" class="mt-0 ml-n4">
        <v-img :src="getImage(image)"> </v-img>
      </v-list-item-avatar>
      <v-list-item-content class="align-self-start">
        <v-list-item-title>
          {{ name }}
        </v-list-item-title>
        <v-rating length="5" size="16" dense :value="rating"></v-rating>
        <div class="text">
          <v-list-item-action-text>
            {{ description | truncate(115) }}
          </v-list-item-action-text>
        </div>
      </v-list-item-content>
    </v-list-item>
  </v-card>
</template>

<script>
import { api } from "@/api";
export default {
  props: {
    name: String,
    slug: String,
    description: String,
    rating: Number,
    image: String,
    route: {
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

.text-top {
  align-self: start !important;
}
</style>