<template>
  <v-container>
    <CardSection
      :sortable="true"
      :title="title"
      :recipes="recipes"
      :card-limit="9999"
      @sort="sortAZ"
      @sort-recent="sortRecent"
    />
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
    };
  },
  computed: {
    currentCategory() {
      return this.$route.params.category;
    },
  },
  watch: {
    async currentCategory() {
      this.getRecipes();
    },
  },
  mounted() {
    this.getRecipes();
  },
  methods: {
    async getRecipes() {
      let data = await api.categories.getRecipesInCategory(this.currentCategory);
      this.title = data.name;
      this.recipes = data.recipes;
    },
    sortAZ() {
      this.recipes.sort((a, b) => (a.name > b.name ? 1 : -1));
    },
    sortRecent() {
      this.recipes.sort((a, b) => (a.dateAdded > b.dateAdded ? -1 : 1));
    },
  },
};
</script>

<style></style>
