<template>
  <v-autocomplete
    :items="items"
    :loading="isLoading"
    v-model="selected"
    clearable
    return
    dense
    hide-details
    hide-selected
    item-text="slug"
    label="Search for a Recipe"
    single-line
    @keyup.enter.native="moreInfo(selected)"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-title>
          Search for your Favorite
          <strong>Recipe</strong>
        </v-list-item-title>
      </v-list-item>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-avatar
        color="primary"
        class="headline font-weight-light white--text"
      >
        <v-img :src="getImage(item.image)"></v-img>
      </v-list-item-avatar>
      <v-list-item-content @click="moreInfo(item.slug)">
        <v-list-item-title v-text="item.name"></v-list-item-title>
      </v-list-item-content>
    </template>
  </v-autocomplete>
</template>

<script>
import utils from "../../utils";

export default {
  data: () => ({
    selected: null,
    isLoading: false,
  }),

  computed: {
    items() {
      return this.$store.getters.getRecentRecipes;
    },
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