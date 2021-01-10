<template>
  <v-card-text>
    <p>
      You can import recipes from either a zip file or a directory located in
      the /app/data/migraiton/ folder. Please review the documentation to ensure
      your directory structure matches what is expected
    </p>
    <v-form ref="form">
      <v-row align="center">
        <v-col cols="12" md="5" sm="5">
          <v-select
            :items="availableImports"
            v-model="selectedImport"
            label="Nextcloud Data"
            :rules="[rules.required]"
          ></v-select>
        </v-col>
        <v-col cols="12" md="2" sm="2">
          <v-btn text color="info" @click="importRecipes"> Migrate </v-btn>
        </v-col>
      </v-row>
    </v-form>
    <SuccessFailureAlert
      success-header="Successfully Imported from Nextcloud"
      :success="successfulImports"
      failed-header="Failed Imports"
      :failed="failedImports"
    />
  </v-card-text>
</template>

<script>
import api from "../../../api";
import SuccessFailureAlert from "../../UI/SuccessFailureAlert";
export default {
  components: {
    SuccessFailureAlert,
  },
  data() {
    return {
      successfulImports: [],
      failedImports: [],
      availableImports: [],
      selectedImport: null,
      rules: {
        required: (v) => !!v || "Selection Required",
      },
    };
  },
  async mounted() {
    this.availableImports = await api.migrations.getNextcloudImports();
  },
  methods: {
    async importRecipes() {
      if (this.$refs.form.validate()) {
        this.$emit("loading");
        let data = await api.migrations.importNextcloud(this.selectedImport);

        this.successfulImports = data.successful;
        this.failedImports = data.failed;
        this.$emit("finished");
      }
    },
  },
};
</script>

<style>
</style>