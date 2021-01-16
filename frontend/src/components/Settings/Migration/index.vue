<template>
  <v-card :loading="loading">
    <v-card-title class="headline"> {{$t('migration.recipe-migration')}} </v-card-title>
    <v-divider></v-divider>

    <v-tabs v-model="tab">
      <v-tab>Chowdown</v-tab>
      <v-tab>Nextcloud Recipes</v-tab>

      <v-tab-item>
        <ChowdownCard @loading="loading = true" @finished="finished" />
      </v-tab-item>
      <v-tab-item>
        <NextcloudCard @loading="loading = true" @finished="finished" />
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>


<script>
import ChowdownCard from "./ChowdownCard";
import NextcloudCard from "./NextcloudCard";
// import SuccessFailureAlert from "../../UI/SuccessFailureAlert";
// import TimePicker from "./Webhooks/TimePicker";
export default {
  components: {
    ChowdownCard,
    NextcloudCard,
  },
  data() {
    return {
      tab: null,
      loading: false,
    };
  },
  methods: {
    finished() {
      this.loading = false;
      this.$store.dispatch("requestRecentRecipes");
    },
  },
};
</script>

<style>
</style>