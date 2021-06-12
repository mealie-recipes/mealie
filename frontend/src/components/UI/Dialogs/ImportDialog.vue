<template>
  <div class="text-center">
    <BaseDialog
      :title="name"
      titleIcon="mdi-database"
      :submit-text="$t('general.import')"
      :loading="loading"
      ref="baseDialog"
      @submit="raiseEvent"
    >
      <v-card-subtitle class="mb-n3 mt-3" v-if="date"> {{ $d(new Date(date), "medium") }} </v-card-subtitle>
      <v-divider></v-divider>

      <v-card-text>
        <ImportOptions @update-options="updateOptions" class="mt-5 mb-2" />

        <v-divider></v-divider>

        <v-checkbox
          dense
          :label="$t('settings.remove-existing-entries-matching-imported-entries')"
          v-model="forceImport"
        ></v-checkbox>
      </v-card-text>

      <v-divider></v-divider>
      <template v-slot:extra-buttons>
        <TheDownloadBtn :download-url="downloadUrl">
          <template v-slot:default="{ downloadFile }">
            <v-btn class="mr-1" color="info" @click="downloadFile">
              <v-icon left> mdi-download </v-icon>
              {{ $t("general.download") }}
            </v-btn>
          </template>
        </TheDownloadBtn>
      </template>
    </BaseDialog>
  </div>
</template>

<script>
const IMPORT_EVENT = "import";
import { api } from "@/api";
import BaseDialog from "./BaseDialog";
import ImportOptions from "@/components/FormHelpers/ImportOptions";
import TheDownloadBtn from "@/components/UI/Buttons/TheDownloadBtn.vue";
import { API_ROUTES } from "@/api/apiRoutes";
export default {
  components: { ImportOptions, TheDownloadBtn, BaseDialog },
  props: {
    name: {
      default: "Backup Name",
    },
    date: {
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
  computed: {
    downloadUrl() {
      return API_ROUTES.backupsFileNameDownload(this.name);
    },
  },
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
