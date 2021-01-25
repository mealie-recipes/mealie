<template>
  <div>
    <CardSection
      v-if="pageSettings.showRecent"
      title="Recent"
      :recipes="recentRecipes"
    />
    <CardSection
      v-for="section in recipeByCategory"
      :key="section.title"
      :title="section.title"
      :recipes="section.recipes"
      :limit="pageSettings.showLimit"
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
    recentRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
    pageSettings() {
      return this.$store.getters.getHomePageSettings;
    },
  },
  methods: {
    getRecentRecipes() {
      this.$store.dispatch("requestRecentRecipes");
    },
  },
};
</script>

<style>
</style>