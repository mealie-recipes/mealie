<template>
  <v-container>
    <CategorySidebar />
    <CardSection
      v-if="showRecent"
      :title="$t('page.recent')"
      :recipes="recentRecipes"
      :card-limit="showLimit"
    />
    <CardSection
      :sortable="true"
      v-for="(section, index) in recipeByCategory"
      :key="section.name + section.position"
      :title="section.name"
      :recipes="section.recipes"
      :card-limit="showLimit"
      @sort="sortAZ(index)"
      @sort-recent="sortRecent(index)"
    />
  </v-container>
</template>

<script>
import api from "@/api";
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
      let recipes = this.$store.getters.getRecentRecipes;
      return recipes.sort((a, b) => (a.dateAdded > b.dateAdded ? -1 : 1));
    },
  },
  async mounted() {
    await this.buildPage();
    this.recipeByCategory.sort((a, b) => a.position - b.position);
  },
  methods: {
    async buildPage() {
      this.homeCategories.forEach(async element => {
        let recipes = await this.getRecipeByCategory(element.slug);
        recipes.position = element.position;
        this.recipeByCategory.push(recipes);
      });
    },
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