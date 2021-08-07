
<template>
  <div>
    <ImportSummaryDialog ref="report" />
    <AdminBackupImportDialog
      ref="import_dialog"
      :name="selectedName"
      :date="selectedDate"
      @import="importBackup"
      @delete="deleteBackup"
    />
    <BaseDialog
      ref="deleteBackupConfirm"
      :title="$t('settings.backup.delete-backup')"
      :message="$t('general.confirm-delete-generic')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="emitDelete()"
    />
    <BaseStatCard :icon="$globals.icons.backupRestore" :color="color">
      <template #after-heading>
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
        <AppButtonUpload url="/api/backups/upload" @uploaded="getAvailableBackups">
          <template #default="{ isSelecting, onButtonClick }">
            <v-btn :loading="isSelecting" class="mx-2" small color="info" @click="onButtonClick">
              <v-icon left> {{ $globals.icons.upload }} </v-icon> {{ $t("general.upload") }}
            </v-btn>
          </template>
        </AppButtonUpload>
        <AdminBackupDialog :color="color" />

        <v-btn :loading="loading" class="mx-2" small color="success" @click="createBackup">
          <v-icon left> {{ $globals.icons.create }} </v-icon> {{ $t("general.create") }}
        </v-btn>
      </div>
      <template #bottom>
        <v-virtual-scroll height="290" item-height="70" :items="availableBackups">
          <template #default="{ item }">
            <v-list-item @click.prevent="openDialog(item, btnEvent.IMPORT_EVENT)">
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
                <v-btn large icon @click.stop="openDialog(item, btnEvent.DELETE_EVENT)">
                  <v-icon color="error">{{ $globals.icons.delete }}</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </template>
        </v-virtual-scroll>
      </template>
    </BaseStatCard>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import AdminBackupImportDialog from "./AdminBackupImportDialog.vue";

const IMPORT_EVENT = "import";
const DELETE_EVENT = "delete";

export default defineComponent({
  components: { AdminBackupImportDialog },
  layout: "admin",
  setup() {
    return {};
  },
  data() {
    return {
      color: "accent",
      selectedName: "",
      selectedDate: "",
      loading: false,
      events: [],
      availableBackups: [],
      btnEvent: { IMPORT_EVENT, DELETE_EVENT },
    };
  },
  computed: {
    total() {
      return this.availableBackups.length || 0;
    },
  },
});
</script>

<style scoped>
</style>