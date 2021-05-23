<template>
  <v-card :ripple="false" class="mx-auto" hover :to="`/recipe/${slug}`" @click="$emit('selected')">
    <v-list-item three-line>
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
      <v-list-item-content>
        <v-list-item-title class=" mb-1">{{ name }} </v-list-item-title>
        <v-list-item-subtitle> {{ description }} </v-list-item-subtitle>
        <div class="d-flex justify-center align-center">
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
          <ContextMenu :slug="slug" menu-icon="mdi-dots-horizontal" />
        </div>
      </v-list-item-content>
    </v-list-item>
  </v-card>
</template>

<script>
import ContextMenu from "@/components/Recipe/ContextMenu";
import { api } from "@/api";
export default {
  components: {
    ContextMenu,
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
  data() {
    return {
      fallBackImage: false,
    };
  },
  methods: {
    getImage(slug) {
      return api.recipes.recipeSmallImage(slug, this.image);
    },
  },
};
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
