<template>
  <v-container>
    <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>
    <CardSection
      title-icon=""
      :sortable="true"
      :title="$t('page.all-recipes')"
      :recipes="shownRecipes"
      @sort="assignSorted"
    />
  </v-container>
</template>

<script>
import CardSection from "@/components/UI/CardSection";

export default {
  components: {
    CardSection,
  },
  data() {
    return {
      loading: false,
      sortedResults: [],
    };
  },
  async mounted() {
    if (this.allRecipes.length < 1) {
      this.loading = true;
    }
    await this.$store.dispatch("requestAllRecipes");
    this.loading = false;
  },
  computed: {
    allRecipes() {
      return this.$store.getters.getAllRecipes;
    },
    shownRecipes() {
      if (this.sortedResults.length > 0) {
        return this.sortedResults;
      } else {
        return this.allRecipes;
      }
    },
  },
  methods: {
    assignSorted(val) {
      this.sortedResults = val;
    },
  },
};
</script>

<style></style>
