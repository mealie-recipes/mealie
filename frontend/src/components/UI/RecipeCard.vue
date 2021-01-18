<template>
  <v-hover v-slot="{ hover }" :open-delay="50">
    <v-card
      :class="{ 'on-hover': hover }"
      :elevation="hover ? 12 : 2"
      @click="moreInfo(slug)"
    >
      <v-img height="200" :src="getImage(image)"></v-img>
      <v-card-title class="my-n3 mb-n6">{{ name | truncate(30) }}</v-card-title>

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
          <v-col align="end">
            <v-tooltip top color="secondary" max-width="400" open-delay="50">
              <template v-slot:activator="{ on, attrs }">
                <v-btn color="secondary" v-on="on" v-bind="attrs" text
                  >{{$t('recipe.description')}}</v-btn
                >
              </template>
              <span>{{ description }}</span>
            </v-tooltip>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </v-hover>
</template>

<script>
import utils from "../../utils";
export default {
  props: {
    name: String,
    slug: String,
    description: String,
    rating: Number,
    image: String,
  },
  methods: {
    moreInfo(recipeSlug) {
      this.$router.push(`/recipe/${recipeSlug}`);
    },
    getImage(image) {
      return utils.getImageURL(image);
    },
  },
};
</script>

<style>
</style>