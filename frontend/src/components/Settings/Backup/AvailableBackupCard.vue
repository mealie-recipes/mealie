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
              <v-col cols="12" sm="2">
                <v-icon large color="primary"> mdi-backup-restore </v-icon>
              </v-col>
              <v-col cols="12" sm="10">
                <div>
                  <strong>{{ backup.name }}</strong>
                </div>
                <div>{{ readableTime(backup.date) }}</div>
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
import api from "@/api";
import utils from "@/utils";
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
    readableTime(timestamp) {
      let date = new Date(timestamp);
      return utils.getDateAsText(date);
    },
    async importBackup(data) {
      this.$emit("loading");
      let response = await api.backups.import(data.name, data);

      let failed = response.data.failed;
      let succesful = response.data.successful;

      this.$emit("finished", succesful, failed);
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