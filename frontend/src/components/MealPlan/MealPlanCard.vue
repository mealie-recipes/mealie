<template>
  <v-row>
    <SearchDialog ref="mealselect" @select="setSlug" />
    <v-col
      cols="12"
      sm="12"
      md="6"
      lg="4"
      xl="3"
      v-for="(meal, index) in value"
      :key="index"
    >
      <v-hover v-slot="{ hover }" :open-delay="50">
        <v-card :class="{ 'on-hover': hover }" :elevation="hover ? 12 : 2">
          <v-img
            height="200"
            :src="getImage(meal.slug)"
            @click="openSearch(index)"
          ></v-img>
          <v-card-title class="my-n3 mb-n6">{{ $d( new Date(meal.date), 'short' ) }}</v-card-title>
          <v-card-subtitle> {{ meal.name }}</v-card-subtitle>
        </v-card>
      </v-hover>
    </v-col>
  </v-row>
</template>

<script>
import utils from "@/utils";
import SearchDialog from "../UI/Search/SearchDialog";
export default {
  components: {
    SearchDialog,
  },
  props: {
    value: Array,
  },
  data() {
    return {
      recipeData: [],
      cardData: [],
      activeIndex: 0,
    };
  },
  methods: {
    getImage(slug) {
      if (slug) {
        return utils.getImageURL(slug);
      }
    },
    setSlug(name, slug) {
      let index = this.activeIndex;
      this.value[index]["slug"] = slug;
      this.value[index]["name"] = name;
    },
    openSearch(index) {
      this.activeIndex = index;
      this.$refs.mealselect.open();
    },
  },
};
</script>

<style>
</style>