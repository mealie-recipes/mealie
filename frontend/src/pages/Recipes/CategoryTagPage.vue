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
    currentTag() {
      return this.$route.params.tag;
    },
    TagOrCategory() {
      return this.currentCategory || this.currentTag;
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
    async TagOrCategory() {
      console.log(this.currentCategory, this.currentTag);
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
      if (!this.TagOrCategory === null) return;
      console.log(this.TagOrCategory);

      let data = {};
      if (this.currentCategory) {
        data = await api.categories.getRecipesInCategory(this.TagOrCategory);
      } else {
        data = await api.tags.getRecipesInTag(this.TagOrCategory);
      }
      console.log(data);
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
