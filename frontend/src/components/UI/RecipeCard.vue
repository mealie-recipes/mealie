<template>
  <v-hover v-slot="{ hover }" :open-delay="50">
    <v-card
      :class="{ 'on-hover': hover }"
      :elevation="hover ? 12 : 2"
      :to="route ? `/recipe/${slug}` : ''"
      @click="$emit('click')"
    >
      <v-img height="200" :src="getImage(image)">
        <v-expand-transition v-if="description">
          <div
            v-if="hover"
            class="d-flex transition-fast-in-fast-out secondary v-card--reveal  "
            style="height: 100%;"
          >
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

      <v-card-actions class="">
        <v-row dense align="center">
          <v-col>
            <v-rating
              class="mr-2"
              color="secondary"
              background-color="secondary lighten-3"
              dense
              length="5"
              size="15"
              :value="rating"
            ></v-rating>
          </v-col>
          <v-col></v-col>
          <v-col align="end"> </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </v-hover>
</template>

<script>
import utils from "@/utils";
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
      return utils.getImageURL(image);
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