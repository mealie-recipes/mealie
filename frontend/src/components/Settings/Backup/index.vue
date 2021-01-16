<template>
  <v-card :loading="backupLoading">
    <v-card-title class="headline"> Backup and Exports </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <p>
        Backups are exported in standard JSON format along with all the images
        stored on the file system. In your backup folder you'll find a .zip file
        that contains all of the recipe JSON and images from the database.
        Additionally, if you selected a markdown file, those will also be stored
        in the .zip file. To import a backup, it must be located in your backups
        folder. Automated backups are done each day at 3:00 AM.
      </p>

      <v-row dense align="center">
        <v-col dense cols="12" sm="12" md="4">
          <v-text-field v-model="backupTag" label="Backup Tag"></v-text-field>
        </v-col>
        <v-col cols="12" sm="12" md="3">
          <v-combobox
            auto-select-first
            label="Markdown Template"
            :items="availableTemplates"
            v-model="selectedTemplate"
          ></v-combobox>
        </v-col>
        <v-col dense cols="12" sm="12" md="2">
          <v-btn block text color="accent" @click="createBackup" width="165">
            Backup Recipes
          </v-btn>
        </v-col>
      </v-row>
      <BackupCard
        @loading="backupLoading = true"
        @finished="processFinished"
        :backups="availableBackups"
      />
      <SuccessFailureAlert
        success-header="Successfully Imported"
        :success="successfulImports"
        failed-header="Failed Imports"
        :failed="failedImports"
      />
    </v-card-text>
  </v-card>
</template>

<script>
import api from "../../../api";
import SuccessFailureAlert from "../../UI/SuccessFailureAlert";
import BackupCard from "./BackupCard";

export default {
  components: {
    SuccessFailureAlert,
    BackupCard,
  },
  data() {
    return {
      failedImports: [],
      successfulImports: [],
      backupLoading: false,
      backupTag: null,
      selectedBackup: null,
      selectedTemplate: null,
      availableBackups: [],
      availableTemplates: [],
    };
  },
  mounted() {
    this.getAvailableBackups();
  },
  methods: {
    async getAvailableBackups() {
      let response = await api.backups.requestAvailable();
      this.availableBackups = response.imports;
      this.availableTemplates = response.templates;
    },
    deleteBackup() {
      if (this.$refs.form.validate()) {
        this.backupLoading = true;

        api.backups.delete(this.selectedBackup);
        this.getAvailableBackups();

        this.selectedBackup = null;
        this.backupLoading = false;
      }
    },
    async createBackup() {
      this.backupLoading = true;

      let response = await api.backups.create(this.backupTag, this.templates);

      if (response.status == 201) {
        this.selectedBackup = null;
        this.getAvailableBackups();
        this.backupLoading = false;
      }
    },
    processFinished(successful = null, failed = null) {
      this.getAvailableBackups();
      this.backupLoading = false;
      this.successfulImports = successful;
      this.failedImports = failed;
    },
  },
};
</script>

<style>
</style>