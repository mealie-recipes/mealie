<template>
  <v-container>
    <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>
    <CardSection
      title-icon=""
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

export default {
  components: {
    CardSection,
  },
  data() {
    return {
      loading: false,
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

<style></style>
