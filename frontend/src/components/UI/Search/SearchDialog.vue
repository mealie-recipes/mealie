<template>
  <div class="text-center ">
    <v-dialog
      v-model="dialog"
      :width="isMobile ? undefined : '600'"
      :height="isMobile ? undefined : '0'"
      :fullscreen="isMobile"
      content-class="top-dialog"
    >
      <v-card relative>
        <v-app-bar dark color="primary lighten-1" rounded="0">
          <SearchBar
            ref="mealSearchBar"
            @results="updateResults"
            @selected="emitSelect"
            :show-results="!isMobile"
            :dense="false"
            :nav-on-click="false"
            :autofocus="true"
          />
        </v-app-bar>
        <v-card-text v-if="isMobile">
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
        </v-card-text>
        <v-btn v-if="isMobile" fab bottom @click="dialog = false" class="ma-2">
          <v-icon> mdi-close </v-icon>
        </v-btn>
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
    },
    toggleDialog(open) {
      if (open) {
        this.$router.push("#search");
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

.top-dialog {
  align-self: flex-start;
}
</style>
