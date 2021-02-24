<template>
  <v-card :loading="backupLoading" class="mt-3">
    <v-card-title class="headline">
      {{ $t("settings.backup-and-exports") }}
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <v-row>
        <v-col cols="12" md="6" sm="12">
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
        {{ $t("settings.available-backups") }}
        <span>
          <UploadBtn
            class="mt-1"
            url="/api/backups/upload"
            @uploaded="getAvailableBackups"
          />
        </span>
        <v-spacer></v-spacer>
      </v-card-title>
      <AvailableBackupCard
        @loading="backupLoading = true"
        @finished="processFinished"
        :backups="availableBackups"
      />
      <SuccessFailureAlert
        ref="report"
        :title="$t('settings.backup.backup-restore-report')"
        :success-header="$t('settings.backup.successfully-imported')"
        :success="successfulImports"
        :failed-header="$t('settings.backup.failed-imports')"
        :failed="failedImports"
      />
      <ImportSummaryDialog ref="report" :import-data="importData" />
    </v-card-text>
  </v-card>
</template>

<script>
import api from "@/api";
import SuccessFailureAlert from "@/components/UI/SuccessFailureAlert";
import ImportSummaryDialog from "@/components/Admin/Backup/ImportSummaryDialog";
import UploadBtn from "@/components/UI/UploadBtn";
import AvailableBackupCard from "@/components/Admin/Backup/AvailableBackupCard";
import NewBackupCard from "@/components/Admin/Backup/NewBackupCard";

export default {
  components: {
    SuccessFailureAlert,
    UploadBtn,
    AvailableBackupCard,
    NewBackupCard,
    ImportSummaryDialog,
  },
  data() {
    return {
      failedImports: [],
      successfulImports: [],
      backupLoading: false,
      availableBackups: [],
      importData: [],
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
    processFinished(data) {
      this.getAvailableBackups();
      this.backupLoading = false;
      this.$refs.report.open(data);
    },
  },
};
</script>

<style>
</style>