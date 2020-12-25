<template>
  <v-row>
    <MealSelect
      :forceDialog="dialog"
      @close="dialog = false"
      @select="setSlug($event)"
    />
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
            @click="selectRecipe(index)"
          ></v-img>
          <v-card-title class="my-n3 mb-n6">{{ meal.dateText }}</v-card-title>
          <v-card-subtitle> {{ meal.slug }}</v-card-subtitle>
        </v-card>
      </v-hover>
    </v-col>
  </v-row>
</template>

<script>
import utils from "../../utils";
import MealSelect from "./MealSelect";
export default {
  components: {
    MealSelect,
  },
  props: {
    value: Array,
  },
  data() {
    return {
      recipeData: [],
      cardData: [],
      activeIndex: 0,
      dialog: false,
    };
  },
  methods: {
    getImage(slug) {
      if (slug) {
        return utils.getImageURL(slug);
      }
    },
    setSlug(slug) {
      let index = this.activeIndex;
      this.value[index]["slug"] = slug;
    },
    selectRecipe(index) {
      this.activeIndex = index;
      this.dialog = true;
    },
    getProperty(index, property) {
      try {
        return this.recipeData[index][property];
      } catch {
        return null;
      }
    },
  },
};
</script>

<style>
</style>