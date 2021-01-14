<template>
  <v-card-text>
    <p>
      Currently Chowdown via public Repo URL is the only supported type of
      migration
    </p>
    <v-form ref="form">
      <v-row dense align="center">
        <v-col cols="12" md="5" sm="5">
          <v-text-field
            v-model="repo"
            label="Chowdown Repo URL"
            :rules="[rules.required]"
          >
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
</template>

<script>
import api from "../../../api";
// import SuccessFailureAlert from "../../UI/SuccessFailureAlert";
// import TimePicker from "./Webhooks/TimePicker";
export default {
  data() {
    return {
      processRan: false,
      failedImages: [],
      failedRecipes: [],
      repo: "",
      rules: {
        required: (v) => !!v || "Selection Required",
      },
    };
  },
  methods: {
    async importRepo() {
      if (this.$refs.form.validate()) {
        this.$emit("loading");
        let response = await api.migrations.migrateChowdown(this.repo);
        this.failedImages = response.failedImages;
        this.failedRecipes = response.failedRecipes;
        this.$emit("finished");
        this.processRan = true;
      }
    },
  },
};
</script>

<style>
</style>