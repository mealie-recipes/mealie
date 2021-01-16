<template>
  <div>
    <ImportDialog
      :name="selectedName"
      :date="selectedDate"
      ref="import_dialog"
    />
    <v-row>
      <v-col
        :sm="6"
        :md="6"
        :lg="3"
        :xl="3"
        v-for="backup in backups"
        :key="backup.name"
      >
        <v-card @click="openDialog(backup)">
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" sm="2">
                <v-icon color="primary"> mdi-backup-restore </v-icon>
              </v-col>
              <v-col cols="12" sm="10">
                <div>
                  <strong>{{ backup.name }}</strong>
                </div>
                <div>{{ backup.date }}</div>
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
export default {
  props: {
    backups: Object,
  },
  components: {
    ImportDialog,
  },
  data() {
    return {
      selectedName: "",
      selectedDate: "",
      // backups: [
      //   { name: "Backup 1", date: " August 23rd" },
      //   { name: "Backup 2", date: " August 24rd" },
      //   { name: "Backup 3", date: " August 25rd" },
      //   { name: "Backup 4", date: " August 25rd" },
      // ],
    };
  },
  methods: {
    openDialog(backup) {
      this.selectedDate = backup.date;
      this.selectedName = backup.name;
      this.$refs.import_dialog.open();
    },
  },
};
</script>

<style>
</style>