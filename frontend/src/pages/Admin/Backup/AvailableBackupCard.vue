<template>
  <div>
    <ImportDialog
      :name="selectedName"
      :date="selectedDate"
      ref="import_dialog"
      @import="importBackup"
      @delete="deleteBackup"
    />
    <v-row>
      <v-col
        :cols="12"
        :sm="6"
        :md="6"
        :lg="4"
        :xl="4"
        v-for="backup in backups"
        :key="backup.name"
      >
        <v-card hover outlined @click="openDialog(backup)">
          <v-card-text>
            <v-row align="center">
              <v-col cols="2">
                <v-icon large color="primary">mdi-backup-restore</v-icon>
              </v-col>
              <v-col cols="10">
                <div class="text-truncate">
                  <strong>{{ backup.name }}</strong>
                </div>
                <div class="text-truncate">{{ $d(new Date(backup.date), "medium") }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import ImportDialog from "./ImportDialog";
import { api } from "@/api";
export default {
  props: {
    backups: Array,
  },
  components: {
    ImportDialog,
  },
  data() {
    return {
      selectedName: "",
      selectedDate: "",
      loading: false,
    };
  },
  methods: {
    openDialog(backup) {
      this.selectedDate = this.readableTime(backup.date);
      this.selectedName = backup.name;
      this.$refs.import_dialog.open();
    },
    async importBackup(data) {
      this.$emit("loading");
      let response = await api.backups.import(data.name, data);

      let importData = response.data;

      this.$emit("finished", importData);
    },
    deleteBackup(data) {
      this.$emit("loading");

      api.backups.delete(data.name);
      this.selectedBackup = null;
      this.backupLoading = false;

      this.$emit("finished");
    },
  },
};
</script>

<style>
</style>