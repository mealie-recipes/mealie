<template>
  <div>
    <v-row justify="center">
      <v-col cols="1"> </v-col>
      <v-col>
        <SearchBar @results="updateResults" :show-results="false" />
      </v-col>
      <v-col cols="2">
        <v-btn icon>
          <v-icon large> mdi-filter </v-icon>
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="searchResults">
      <v-col
        :sm="6"
        :md="6"
        :lg="4"
        :xl="3"
        v-for="item in searchResults.slice(0, 10)"
        :key="item.item.name"
      >
        <RecipeCard
          :name="item.item.name"
          :description="item.item.description"
          :slug="item.item.slug"
          :rating="item.item.rating"
          :image="item.item.image"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import SearchBar from "../components/UI/SearchBar";
import RecipeCard from "../components/UI/RecipeCard";
export default {
  components: {
    SearchBar,
    RecipeCard,
  },
  data() {
    return {
      searchResults: [],
    };
  },
  methods: {
    updateResults(results) {
      this.searchResults = results;
    },
  },
};
</script>

<style>
</style>