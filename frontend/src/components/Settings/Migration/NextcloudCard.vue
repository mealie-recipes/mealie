<template>
  <v-card-text>
    <p>
      You can import recipes from either a zip file or a directory located in
      the /app/data/migraiton/ folder. Please review the documentation to ensure
      your directory structure matches what is expected
    </p>
    <v-form ref="form">
      <v-row align="center">
        <v-col cols="12" md="5" sm="12">
          <v-select
            :items="availableImports"
            v-model="selectedImport"
            label="Nextcloud Data"
            :rules="[rules.required]"
          ></v-select>
        </v-col>
        <v-col cols="12" md="2" sm="12">
          <v-btn text color="info" @click="importRecipes"> Migrate </v-btn>
        </v-col>
        <v-col cols="12" md="1" sm="12">
          <v-btn text color="error" @click="deleteImportValidation">
            Delete
          </v-btn>
          <Confirmation
            title="Delete Data"
            message="Are you sure you want to delete this migration data?"
            color="error"
            icon="mdi-alert-circle"
            ref="deleteThemeConfirm"
            v-on:confirm="deleteImport()"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="5" sm="12">
          <UploadMigrationButton @uploaded="getAvaiableImports" />
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
import UploadMigrationButton from "./UploadMigrationButton";
import Confirmation from "../../UI/Confirmation";
export default {
  components: {
    SuccessFailureAlert,
    UploadMigrationButton,
    Confirmation,
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
    this.getAvaiableImports();
  },
  methods: {
    async getAvaiableImports() {
      this.availableImports = await api.migrations.getNextcloudImports();
    },
    async importRecipes() {
      if (this.$refs.form.validate()) {
        this.$emit("loading");
        let data = await api.migrations.importNextcloud(this.selectedImport);

        this.successfulImports = data.successful;
        this.failedImports = data.failed;
        this.$emit("finished");
      }
    },
    deleteImportValidation() {
      if (this.$refs.form.validate()) {
        this.$refs.deleteThemeConfirm.open();
      }
    },
    async deleteImport() {
      await api.migrations.delete(this.selectedImport);
      this.getAvaiableImports();
    },
  },
};
</script>

<style>
</style>