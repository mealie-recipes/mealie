<template>
  <v-card :loading="backupLoading" class="mt-3">
    <v-card-title class="headline">
      {{ $t("settings.backup-and-exports") }}
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="6" ss="12">
          <NewBackupCard @created="processFinished" />
        </v-col>
        <v-col cols="12" md="6" sm="12">
          <p>
            {{ $t("settings.backup-info") }}
          </p>
        </v-col>
      </v-row>
      <v-divider class="my-3"></v-divider>
      <v-card-title class="mt-n6">
        Available Backups
        <v-spacer></v-spacer>
        <span>
          <v-btn color="success" text class="ma-2 white--text">
            Upload
            <v-icon right dark> mdi-cloud-upload </v-icon>
          </v-btn>
        </span>
      </v-card-title>
      <AvailableBackupCard
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
import AvailableBackupCard from "./AvailableBackupCard";
import NewBackupCard from "./NewBackupCard";

export default {
  components: {
    SuccessFailureAlert,
    AvailableBackupCard,
    NewBackupCard,
  },
  data() {
    return {
      failedImports: [],
      successfulImports: [],
      backupLoading: false,
      availableBackups: [],
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