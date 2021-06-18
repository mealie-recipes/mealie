<template>
  <div>
    <ImportSummaryDialog ref="report" />
    <ImportDialog
      :name="selectedName"
      :date="selectedDate"
      ref="import_dialog"
      @import="importBackup"
      @delete="deleteBackup"
    />
    <StatCard :icon="$globals.icons.backupRestore" :color="color">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <h2 class="body-3 grey--text font-weight-light">
            {{ $t("settings.backup-and-exports") }}
          </h2>

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ total }}</small>
          </h3>
        </div>
      </template>
      <div class="d-flex row py-3 justify-end">
        <TheUploadBtn url="/api/backups/upload" @uploaded="getAvailableBackups">
          <template v-slot="{ isSelecting, onButtonClick }">
            <v-btn :loading="isSelecting" class="mx-2" small color="info" @click="onButtonClick">
              <v-icon left> {{ $globals.icons.upload }} </v-icon> {{ $t("general.upload") }}
            </v-btn>
          </template>
        </TheUploadBtn>
        <BackupDialog :color="color" />

        <v-btn :loading="loading" class="mx-2" small color="success" @click="createBackup">
          <v-icon left> {{ $globals.icons.create }} </v-icon> {{ $t("general.create") }}
        </v-btn>
      </div>
      <template v-slot:bottom>
        <v-virtual-scroll height="290" item-height="70" :items="availableBackups">
          <template v-slot:default="{ item }">
            <v-list-item @click.prevent="openDialog(item)">
              <v-list-item-avatar>
                <v-icon large dark :color="color">
                  {{ $globals.icons.database }}
                </v-icon>
              </v-list-item-avatar>

              <v-list-item-content>
                <v-list-item-title v-text="item.name"></v-list-item-title>

                <v-list-item-subtitle>
                  {{ $d(Date.parse(item.date), "medium") }}
                </v-list-item-subtitle>
              </v-list-item-content>

              <v-list-item-action class="ml-auto">
                <v-btn large icon @click.stop="deleteBackup(item.name)">
                  <v-icon color="error">{{ $globals.icons.delete }}</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </template>
    </StatCard>
  </div>
</template>

<script>
import TheUploadBtn from "@/components/UI/Buttons/TheUploadBtn";
import ImportSummaryDialog from "@/components/ImportSummaryDialog";
import { api } from "@/api";
import StatCard from "@/components/UI/StatCard";
import BackupDialog from "@/components/UI/Dialogs/BackupDialog";
import ImportDialog from "@/components/UI/Dialogs/ImportDialog";
export default {
  components: { StatCard, ImportDialog, TheUploadBtn, ImportSummaryDialog, BackupDialog },
  data() {
    return {
      color: "accent",
      selectedName: "",
      selectedDate: "",
      loading: false,
      events: [],
      availableBackups: [],
    };
  },
  computed: {
    total() {
      return this.availableBackups.length;
    },
  },
  created() {
    this.getAvailableBackups();
  },
  methods: {
    async getAvailableBackups() {
      const response = await api.backups.requestAvailable();
      this.availableBackups = response.imports;
    },

    async deleteBackup(name) {
      this.loading = true;
      await api.backups.delete(name);
      this.loading = false;
      this.getAvailableBackups();
    },

    openDialog(backup) {
      this.selectedDate = backup.date;
      this.selectedName = backup.name;
      this.$refs.import_dialog.open();
    },

    async importBackup(data) {
      this.$refs.report.open(data);
    },

    async createBackup() {
      this.loading = true;

      let data = {
        tag: this.tag,
        options: {},
        templates: [],
      };

      if (await api.backups.create(data)) {
        this.getAvailableBackups();
      }
      this.loading = false;
    },
  },
};
</script>

<style lang="scss" scoped>
</style>