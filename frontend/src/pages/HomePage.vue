<template>
  <div>
    <CardSection
      v-if="pageSettings.showRecent"
      title="Recent"
      :recipes="recentRecipes"
      :card-limit="pageSettings.showLimit"
    />
    <CardSection
      v-for="(section, index) in recipeByCategory"
      :key="index"
      :title="section.title"
      :recipes="section.recipes"
      :card-limit="pageSettings.showLimit"
      @sort="sortAZ(index)"
      @sort-recent="sortRecent(index)"
    />
  </div>
</template>

<script>
import CardSection from "../components/UI/CardSection";
export default {
  components: {
    CardSection,
  },
  data() {
    return {
      recipeByCategory: [
        {
          title: "Title 1",
          recipes: this.$store.getters.getRecentRecipes,
        },
        {
          title: "Title 2",
          recipes: this.$store.getters.getRecentRecipes,
        },
      ],
    };
  },
  computed: {
    pageSettings() {
      return this.$store.getters.getHomePageSettings;
    },
    recentRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
  },
  methods: {
    getRecentRecipes() {
      this.$store.dispatch("requestRecentRecipes");
    },
    sortAZ(index) {
      this.recipeByCategory[index].recipes.sort((a, b) =>
        a.name > b.name ? 1 : -1
      );
      console.log(this.recipeByCategory[index].recipes);
    },
    sortRecent(index) {
      this.recipeByCategory[index].recipes.sort((a, b) =>
        a.dateAdded > b.dateAdded ? -1 : 1
      );
      console.log(this.recipeByCategory[index].recipes);
    },
  },
};
</script>

<style>
</style>