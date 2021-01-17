<template>
  <v-card :loading="backupLoading" class="mt-3">
    <v-card-title class="headline">
      {{ $t("settings.backup-and-exports") }}
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="6" ss="12">
          <NewBackupCard />
        </v-col>
        <v-col cols="12" md="6" sm="12">
          <p>
            {{ $t("settings.backup-info") }}
          </p>
        </v-col>
      </v-row>
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