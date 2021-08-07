<template>
  <div class="text-center">
    <BaseDialog
      ref="baseDialog"
      :title="name"
      :title-icon="$globals.icons.database"
      :submit-text="$t('general.import')"
      :loading="loading"
      @submit="raiseEvent"
    >
      <v-card-subtitle v-if="date" class="mb-n3 mt-3"> {{ $d(new Date(date), "medium") }} </v-card-subtitle>
      <v-divider></v-divider>

      <v-card-text>
        <AdminBackupImportOptions class="mt-5 mb-2" @update-options="updateOptions" />

        <v-divider></v-divider>

        <v-checkbox
          v-model="forceImport"
          dense
          :label="$t('settings.remove-existing-entries-matching-imported-entries')"
        ></v-checkbox>
      </v-card-text>

      <v-divider></v-divider>
      <template #extra-buttons>
        <!-- <TheDownloadBtn :download-url="downloadUrl">
          <template #default="{ downloadFile }">
            <v-btn class="mr-1" color="info" @click="downloadFile">
              <v-icon left> {{ $globals.icons.download }}</v-icon>
              {{ $t("general.download") }}
            </v-btn>
          </template>
        </TheDownloadBtn> -->
      </template>
    </BaseDialog>
  </div>
</template>

<script>
import { api } from "@/api";
import AdminBackupImportOptions from "./AdminBackupImportOptions";
const IMPORT_EVENT = "import";
export default {
  components: { AdminBackupImportOptions },
  props: {
    name: {
      type: String,
      default: "Backup Name",
    },
    date: {
      type: String,
      default: "Backup Date",
    },
  },
  data() {
    return {
      loading: false,
      options: {
        recipes: true,
        settings: true,
        themes: true,
        users: true,
        groups: true,
      },
      dialog: false,
      forceImport: false,
      rebaseImport: false,
      downloading: false,
    };
  },
  // computed: {
  //   downloadUrl() {
  //     return API_ROUTES.backupsFileNameDownload(this.name);
  //   },
  // },
  methods: {
    updateOptions(options) {
      this.options = options;
    },
    open() {
      this.dialog = true;
      this.$refs.baseDialog.open();
    },
    close() {
      this.dialog = false;
    },
    async raiseEvent() {
      const eventData = {
        name: this.name,
        force: this.forceImport,
        rebase: this.rebaseImport,
        recipes: this.options.recipes,
        settings: this.options.settings,
        themes: this.options.themes,
        users: this.options.users,
        groups: this.options.groups,
        notifications: this.options.notifications,
      };
      this.loading = true;
      const importData = await this.importBackup(eventData);

      this.$emit(IMPORT_EVENT, importData);
      this.loading = false;
    },
    async importBackup(data) {
      this.loading = true;
      const response = await api.backups.import(data.name, data);
      if (response) {
        return response.data;
      }
    },
  },
};
</script>

<style></style>
