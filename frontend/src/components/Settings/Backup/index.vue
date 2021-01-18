<template>
  <v-card :loading="backupLoading" class="mt-3">
    <v-card-title class="headline">
      {{$t('settings.backup-and-exports')}}
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <p>
        {{$t('settings.backup-info')}}
      </p>

      <v-row dense align="center">
        <v-col dense cols="12" sm="12" md="4">
          <v-text-field v-model="backupTag" :label="$t('settings.backup-tag')"></v-text-field>
        </v-col>
        <v-col cols="12" sm="12" md="3">
          <v-combobox
            auto-select-first
            :label="$t('settings.markdown-template')"
            :items="availableTemplates"
            v-model="selectedTemplate"
          ></v-combobox>
        </v-col>
        <v-col dense cols="12" sm="12" md="2">
          <v-btn block text color="accent" @click="createBackup" width="165">
            {{$t('settings.backup-recipes')}}
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