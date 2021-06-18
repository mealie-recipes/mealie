<template>
  <v-container>
    <CardSection
      :sortable="true"
      :title-icon="$globals.icons.user"
      :title="userData.username"
      :recipes="shownRecipes"
      @sort="assignSorted"
    />
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
      userData: {},
      sortedResults: [],
    };
  },
  computed: {
    shownRecipes() {
      if (this.sortedResults.length > 0) {
        return this.sortedResults;
      } else {
        return this.userData.favoriteRecipes;
      }
    },
  },
  async created() {
    this.userData = await api.users.getFavorites(this.$route.params.id);
    this.sortedResults = [];
  },
  methods: {
    assignSorted(val) {
      this.sortedResults = val.slice();
    },
  },
};
</script>

<style></style>
