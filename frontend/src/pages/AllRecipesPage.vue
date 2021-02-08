<template>
  <div>
    <CategorySidebar />
    <CardSection
      :sortable="true"
      title="All Recipes"
      :recipes="allRecipes"
      :card-limit="9999"
      @sort="sortAZ"
      @sort-recent="sortRecent"
    />
  </div>
</template>

<script>
import CardSection from "../components/UI/CardSection";
import CategorySidebar from "../components/UI/CategorySidebar";
export default {
  components: {
    CardSection,
    CategorySidebar,
  },
  data() {
    return {};
  },
  computed: {
    allRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
  },
  methods: {
    sortAZ() {
      this.allRecipes.sort((a, b) => (a.name > b.name ? 1 : -1));
    },
    sortRecent() {
      this.allRecipes.sort((a, b) => (a.dateAdded > b.dateAdded ? -1 : 1));
    },
  },
};
</script>

<style>
</style>