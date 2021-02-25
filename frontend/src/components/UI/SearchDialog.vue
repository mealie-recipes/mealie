<template>
  <div class="text-center">
    <v-dialog v-model="dialog" height="100%" max-width="1200">
      <v-card min-height="725" height="100%">
        <v-card-text>
          <v-card-title></v-card-title>
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
              v-for="item in searchResults.slice(0, 24)"
              :key="item.item.name"
            >
              <RecipeCard
                :route="false"
                :name="item.item.name"
                :description="item.item.description"
                :slug="item.item.slug"
                :rating="item.item.rating"
                :image="item.item.image"
                @click="emitSelect(item.item.name, item.item.slug)"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import SearchBar from "../UI/SearchBar";
import RecipeCard from "../UI/RecipeCard";
export default {
  components: {
    SearchBar,
    RecipeCard,
  },
  data() {
    return {
      searchResults: null,
      dialog: false,
    };
  },
  methods: {
    updateResults(results) {
      this.searchResults = results;
    },
    emitSelect(name, slug) {
      this.$emit("select", name, slug);
      this.dialog = false;
    },
    open() {
      this.dialog = true;
    },
  },
};
</script>

<style>
</style>