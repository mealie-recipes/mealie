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
    <StatCard icon="mdi-backup-restore" :color="color">
      <template v-slot:after-heading>
        <div class="ml-auto text-right">
          <div class="body-3 grey--text font-weight-light" v-text="'Backups'" />

          <h3 class="display-2 font-weight-light text--primary">
            <small> {{ total }}</small>
          </h3>
        </div>
      </template>
      <div class="d-flex row py-3 justify-end">
        <TheUploadBtn url="/api/backups/upload" @uploaded="getAvailableBackups">
          <template v-slot="{ isSelecting, onButtonClick }">
            <v-btn :loading="isSelecting" class="mx-2" small :color="color" @click="onButtonClick">
              <v-icon left> mdi-cloud-upload </v-icon> Upload
            </v-btn>
          </template>
        </TheUploadBtn>
        <v-btn :loading="loading" class="mx-2" small :color="color" @click="createBackup">
          <v-icon left> mdi-plus </v-icon> Create
        </v-btn>
      </div>
      <template v-slot:bottom>
        <v-virtual-scroll height="290" item-height="70" :items="availableBackups">
          <template v-slot:default="{ item }">
            <v-list-item @click.prevent="openDialog(item)">
              <v-list-item-avatar>
                <v-icon large dark :color="color">
                  mdi-backup-restore
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
                  <v-icon color="error">mdi-delete</v-icon>
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
import StatCard from "./StatCard";
import ImportDialog from "../Backup/ImportDialog";
export default {
  components: { StatCard, ImportDialog, TheUploadBtn, ImportSummaryDialog },
  data() {
    return {
      color: "secondary",
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
  mounted() {
    this.getAvailableBackups();
  },
  methods: {
    async getAvailableBackups() {
      const response = await api.backups.requestAvailable();
      this.availableBackups = response.imports;
      console.log(this.availableBackups);
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
      this.loading = true;
      const response = await api.backups.import(data.name, data);
      if (response) {
        const importData = response.data;
        this.$refs.report.open(importData);
      }
      this.loading = false;
    },

    async createBackup() {
      this.loading = true;

      let data = {
        tag: this.tag,
        options: {
          recipes: true,
          settings: true,
          themes: true,
          users: true,
          groups: true,
        },
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