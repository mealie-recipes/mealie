<template>
  <v-card :loading="loading">
    <v-card-title class="secondary white--text mt-1">
      Recipe Migration
    </v-card-title>
    <v-card-text>
      <p>
        Currently Chowdown via public Repo URL is the only supported type of
        migration
      </p>
      <v-form>
        <v-row dense align="center">
          <v-col cols="12" md="5" sm="5">
            <v-text-field v-model="repo" label="Chowdown Repo URL">
            </v-text-field>
          </v-col>
          <v-col cols="12" md="4" sm="5">
            <v-btn text color="info" @click="importRepo"> Migrate </v-btn>
          </v-col>
        </v-row>
      </v-form>
      <v-alert v-if="failedRecipes[1]" outlined dense type="error">
        <h4>Failed Recipes</h4>
        <v-list dense>
          <v-list-item v-for="fail in this.failedRecipes" :key="fail">
            {{ fail }}
          </v-list-item>
        </v-list>
      </v-alert>
      <v-alert v-if="failedImages[1]" outlined dense type="error">
        <h4>Failed Images</h4>
        <v-list dense>
          <v-list-item v-for="fail in this.failedImages" :key="fail">
            {{ fail }}
          </v-list-item>
        </v-list>
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script>
import api from "../../../api";
// import TimePicker from "./Webhooks/TimePicker";
export default {
  data() {
    return {
      processRan: false,
      loading: false,
      failedImages: [],
      failedRecipes: [],
      repo: "",
    };
  },
  methods: {
    async importRepo() {
      this.loading = true;
      let response = await api.migrations.migrateChowdown(this.repo);
      this.failedImages = response.failedImages;
      this.failedRecipes = response.failedRecipes;
      this.loading = false;
      this.processRan = true;
    },
  },
};
</script>

<style>
</style>