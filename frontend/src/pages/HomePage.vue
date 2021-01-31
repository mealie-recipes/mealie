<template>
  <div>
    <CategorySidebar/>

    <CardSection
      v-if="showRecent"
      title="Recent"
      :recipes="recentRecipes"
      :card-limit="showLimit"
    />
    <CardSection
      :sortable="true"
      v-for="(section, index) in recipeByCategory"
      :key="index"
      :title="section.name"
      :recipes="section.recipes"
      :card-limit="showLimit"
      @sort="sortAZ(index)"
      @sort-recent="sortRecent(index)"
    />
  </div>
</template>

<script>
import api from "../api";
import CardSection from "../components/UI/CardSection";
import CategorySidebar from "../components/UI/CategorySidebar";
export default {
  components: {
    CardSection,
    CategorySidebar,
  },
  data() {
    return {
      recipeByCategory: [],
    };
  },
  computed: {
    showRecent() {
      return this.$store.getters.getShowRecent;
    },
    showLimit() {
      return this.$store.getters.getShowLimit;
    },
    homeCategories() {
      return this.$store.getters.getHomeCategories;
    },
    recentRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
  },
  async mounted() {
    this.homeCategories.forEach(async (element) => {
      let recipes = await this.getRecipeByCategory(element);
      this.recipeByCategory.push(recipes);
    });
  },
  methods: {
    async getRecipeByCategory(category) {
      return await api.categories.get_recipes_in_category(category);
    },
    getRecentRecipes() {
      this.$store.dispatch("requestRecentRecipes");
    },
    sortAZ(index) {
      this.recipeByCategory[index].recipes.sort((a, b) =>
        a.name > b.name ? 1 : -1
      );
    },
    sortRecent(index) {
      this.recipeByCategory[index].recipes.sort((a, b) =>
        a.dateAdded > b.dateAdded ? -1 : 1
      );
    },
  },
};
</script>

<style>
</style>