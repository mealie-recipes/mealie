<template>
  <v-card :loading="backupLoading" class="mt-3" min-height="410px">
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
          <v-btn block color="accent" @click="createBackup" width="165">
            {{$t('settings.backup-recipes')}}
          </v-btn>
        </v-col>
      </v-row>

      <v-row dense align="center">
        <v-col dense cols="12" sm="12" md="4">
          <v-form ref="form">
            <v-combobox
              auto-select-first
              :label="$t('settings.select-a-backup-for-import')"
              :items="availableBackups"
              v-model="selectedBackup"
              :rules="[(v) => !!v || $t('settings.backup-selection-is-required')]"
              required
            ></v-combobox>
          </v-form>
        </v-col>
        <v-col dense cols="12" sm="12" md="3" lg="2">
          <v-btn block color="accent" @click="importBackup">
            {{$t('settings.import-backup')}}
          </v-btn>
        </v-col>
        <v-col dense cols="12" sm="12" md="2" lg="2">
          <v-btn block color="error" @click="deleteBackup">
            {{$t('settings.delete-backup')}}
          </v-btn>
        </v-col>
      </v-row>
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

export default {
  components: {
    SuccessFailureAlert,
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
    async importBackup() {
      if (this.$refs.form.validate()) {
        this.backupLoading = true;

        let response = await api.backups.import(this.selectedBackup);
        console.log(response.data);
        this.failedImports = response.data.failed;
        this.successfulImports = response.data.successful;

        this.backupLoading = false;
      }
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

      let response = await api.backups.create(
        this.backupTag,
        this.selectedTemplate
      );

      if (response.status == 201) {
        this.selectedBackup = null;
        this.getAvailableBackups();
        this.backupLoading = false;
      }
    },
  },
};
</script>

<style>
</style>