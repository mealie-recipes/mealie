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
          <TheUploadBtn
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

      <ImportSummaryDialog ref="report" :import-data="importData" />
    </v-card-text>
  </v-card>
</template>

<script>
import { api } from "@/api";
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import ImportSummaryDialog from "@/components/ImportSummaryDialog";
import AvailableBackupCard from "@/pages/Admin/Backup/AvailableBackupCard";
import NewBackupCard from "@/pages/Admin/Backup/NewBackupCard";

export default {
  components: {
    TheUploadBtn,
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