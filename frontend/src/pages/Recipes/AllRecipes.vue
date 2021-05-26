<template>
  <v-container>
    <CardSection
      title-icon=""
      :sortable="true"
      :title="$t('page.all-recipes')"
      :recipes="shownRecipes"
      @sort="assignSorted"
    />
    <v-row class="d-flex">
      <SiteLoader class="mx-auto" v-if="loading" :loading="loading" :size="200" />
    </v-row>
  </v-container>
</template>

<script>
import SiteLoader from "@/components/UI/SiteLoader";
import CardSection from "@/components/UI/CardSection";

export default {
  components: {
    SiteLoader,
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
