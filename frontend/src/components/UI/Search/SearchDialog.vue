<template>
  <div class="text-center ">
    <v-dialog v-model="dialog" class="search-dialog" width="600px" height="0">
      <v-card>
        <v-app-bar dark color="primary">
          <v-toolbar-title class="headline">Search a Recipe</v-toolbar-title>
        </v-app-bar>
        <v-card-text>
          <SearchBar
            @results="updateResults"
            @selected="emitSelect"
            :show-results="true"
            max-width="550px"
            :dense="false"
            :nav-on-click="false"
            :reset-search="dialog"
            :solo="false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import SearchBar from "./SearchBar";
export default {
  components: {
    SearchBar,
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
    emitSelect(slug, name) {
      this.$emit("select", name, slug);
      this.dialog = false;
    },
    open() {
      this.dialog = true;
    },
  },
};
</script>

<style scope>
.search-dialog {
  margin-top: 10%;
  align-items: flex-start;
  justify-content: center;
}
</style>