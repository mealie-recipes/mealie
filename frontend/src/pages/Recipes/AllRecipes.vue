<template>
  <v-container>
    <CategorySidebar />
    <CardSection
      :sortable="true"
      :title="$t('page.all-recipes')"
      :recipes="allRecipes"
      @sort="sortAZ"
      @sort-recent="sortRecent"
    />
  </v-container>
</template>

<script>
import CardSection from "@/components/UI/CardSection";
import CategorySidebar from "@/components/UI/CategorySidebar";
export default {
  components: {
    CardSection,
    CategorySidebar,
  },
  data() {
    return {};
  },
  mounted() {
    this.$store.dispatch("requestAllRecipes");
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