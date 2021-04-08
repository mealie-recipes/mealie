<template>
  <div class="text-center ">
    <v-dialog v-model="dialog" width="600px" height="0" :fullscreen="isMobile">
      <v-card>
        <v-app-bar dark color="primary">
          <v-toolbar-title class="headline">Search a Recipe</v-toolbar-title>
        </v-app-bar>
        <v-card-text>
          <SearchBar
            @results="updateResults"
            @selected="emitSelect"
            :show-results="!isMobile"
            max-width="550px"
            :dense="false"
            :nav-on-click="false"
            :reset-search="dialog"
            :solo="false"
          />
          <div v-if="isMobile">
            <div v-for="recipe in searchResults.slice(0, 7)" :key="recipe.name">
              <MobileRecipeCard
                class="ma-1 px-0"
                :name="recipe.item.name"
                :description="recipe.item.description"
                :slug="recipe.item.slug"
                :rating="recipe.item.rating"
                :image="recipe.item.image"
                :route="true"
                @selected="dialog = false"
              />
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import SearchBar from "./SearchBar";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
export default {
  components: {
    SearchBar,
    MobileRecipeCard,
  },
  data() {
    return {
      searchResults: [],
      dialog: false,
    };
  },
  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
  },
  watch: {
    "$route.hash"(newHash, oldHash) {
      if (newHash === "#mobile-search") {
        this.dialog = true;
      } else if (oldHash === "#mobile-search") {
        this.dialog = false;
      }
    },
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
      this.$router.push("#mobile-search");
    },
    toggleDialog(open) {
      if (open) {
        this.$router.push("#mobile-search");
      } else {
        this.$router.back(); // 😎 back button click
      }
    },
  },
};
</script>

<style scope>
.mobile-dialog {
  align-items: flex-start;
  justify-content: flex-start;
}
</style>