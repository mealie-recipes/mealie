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
    currentTag() {
      return this.$route.params.tag;
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
    async currentTag() {
      this.getRecipes();
      this.sortedResults = [];
    },
  },
  mounted() {
    this.getRecipes();
    this.sortedResults = [];
  },
  methods: {
    async getRecipes() {
      let data = await api.tags.getRecipesInTag(this.currentTag);
      this.title = data.name;
      this.recipes = data.recipes;
    },
    assignSorted(val) {
      console.log(val);
      this.sortedResults = val.slice();
    },
  },
};
</script>

<style></style>
