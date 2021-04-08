<template>
  <v-container>
    <CategorySidebar />
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
import CategorySidebar from "@/components/UI/CategorySidebar";
export default {
  components: {
    CardSection,
    CategorySidebar,
  },
  data() {
    return {
      title: "",
      recipes: [],
    };
  },
  computed: {
    currentTag() {
      return this.$route.params.tag;
    },
  },
  watch: {
    async currentTag() {
      this.getRecipes();
    },
  },
  mounted() {
    this.getRecipes();
  },
  methods: {
    async getRecipes() {
      let data = await api.tags.getRecipesInTag(this.currentTag);
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

<style>
</style>