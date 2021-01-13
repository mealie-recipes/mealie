<template>
  <div>
    <v-text-field
      label="Search"
      v-model="search"
      solo
    ></v-text-field>
    <v-card v-if="search && showResults">
      <v-hover
        square
        v-for="(item, index) in result.slice(0, 5)"
        :key="index"
        v-slot="{ hover }"
      >
        <v-card
          class="color-transition"
          @click="$router.push(`/recipe/${item.item.slug}`)"
          :color="hover ? highlightColor : null"
        >
          <v-row dense no-gutters>
            <v-col cols="12" md="2" sm="6">
              <v-img
                :src="getImage(item.item.image)"
                width="100%"
                height="100%"
                rounded
              >
              </v-img>
            </v-col>
            <v-col cols="12" md="10" sm="6">
              <v-card-title> {{ item.item.name }}</v-card-title>
              <v-card-text> {{ item.item.description }}</v-card-text></v-col
            >
          </v-row>
        </v-card>
      </v-hover>
    </v-card>
  </div>
</template>

<script>
import Fuse from "fuse.js";
import utils from "../../utils";

export default {
  props: {
    showResults: {
      default: false,
    },
  },
  data() {
    return {
      search: "",
      result: [],
      isDark: false,
      options: {
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        maxPatternLength: 32,
        minMatchCharLength: 1,
        keys: ["name", "slug"],
      },
    };
  },
  mounted() {
    this.isDark = this.$store.getters.getIsDark;
  },
  computed: {
    data() {
      return this.$store.getters.getRecentRecipes;
    },
    fuse() {
      return new Fuse(this.data, this.options);
    },
    highlightColor() {
      return this.isDark ? "primary lighten-5" : "primary lighten-5";
    },
  },
  watch: {
    search() {
      if (this.search.trim() === "") this.result = this.list;
      else this.result = this.fuse.search(this.search.trim());
      this.$emit("results", this.result);
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
.color-transition {
  transition: background-color 0.3s ease;
}
</style>