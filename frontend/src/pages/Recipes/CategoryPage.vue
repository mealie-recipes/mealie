<template>
  <v-container>
    <CardSection :sortable="true" :title="title" :recipes="shownRecipes" @sort="assignSorted" />
  </v-container>
</template>

<script>
import { api } from "@/api";
import CardSection from "@/components/UI/CardSection";
export default {
  components: {
    CardSection,
  },
  data() {
    return {
      title: "",
      recipes: [],
      sortedResults: [],
    };
  },
  computed: {
    currentCategory() {
      return this.$route.params.category;
    },
    shownRecipes() {
      if (this.sortedResults.length > 0) {
        return this.sortedResults;
      } else {
        return this.recipes;
      }
    },
  },
  watch: {
    async currentCategory() {
      this.sortedResults = [];
      this.getRecipes();
    },
  },
  mounted() {
    this.getRecipes();
    this.sortedResults = [];
  },
  methods: {
    async getRecipes() {
      let data = await api.categories.getRecipesInCategory(this.currentCategory);
      this.title = data.name;
      this.recipes = data.recipes;
    },
    assignSorted(val) {
      this.sortedResults = val.slice();
    },
  },
};
</script>

<style></style>
