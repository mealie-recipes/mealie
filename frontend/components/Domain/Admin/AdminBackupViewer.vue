
<template>
  <div>
    <BaseDialog
      ref="refImportDialog"
      :title="selectedBackup.name"
      :icon="$globals.icons.database"
      :submit-text="$t('general.import')"
      :loading="loading"
      @submit="restoreBackup"
    >
      <v-card-subtitle v-if="selectedBackup.date" class="mb-n3 mt-3">
        {{ $d(new Date(selectedBackup.date), "medium") }}
      </v-card-subtitle>
      <v-divider></v-divider>
      <v-card-text>
        <AdminBackupImportOptions v-model="importOptions" import-backup class="mt-5 mb-2" />
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      ref="refDeleteConfirmation"
      :title="$t('settings.backup.delete-backup')"
      color="error"
      :icon="$globals.icons.alertCircle"
      @confirm="deleteBackup(selectedBackup.name)"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>
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
        <AppButtonUpload url="/api/backups/upload" @uploaded="refreshBackups">
          <template #default="{ isSelecting, onButtonClick }">
            <v-btn :loading="isSelecting" class="mx-2" small color="info" @click="onButtonClick">
              <v-icon left> {{ $globals.icons.upload }} </v-icon> {{ $t("general.upload") }}
            </v-btn>
          </template>
        </AppButtonUpload>
        <AdminBackupDialog :color="color" />

        <v-btn :loading="loading" class="mx-2" small color="success" @click="createBackup(null)">
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
import { defineComponent, ref } from "@nuxtjs/composition-api";
import AdminBackupImportOptions from "./AdminBackupImportOptions.vue";
import AdminBackupDialog from "./AdminBackupDialog.vue";
import { BackupFile } from "~/api/class-interfaces/backups";
import { useBackups } from "~/composables/use-backups";

const IMPORT_EVENT = "import";
const DELETE_EVENT = "delete";

type EVENTS = "import" | "delete";

export default defineComponent({
  components: { AdminBackupImportOptions, AdminBackupDialog },
  props: {
    availableBackups: {
      type: Array,
      required: true,
    },
    templates: {
      type: Array,
      required: true,
    },
  },
  setup() {
    const refImportDialog = ref();
    const refDeleteConfirmation = ref();

    const { refreshBackups, importBackup, createBackup, deleteBackup } = useBackups();

    return {
      btnEvent: { IMPORT_EVENT, DELETE_EVENT },
      refImportDialog,
      refDeleteConfirmation,
      refreshBackups,
      importBackup,
      createBackup,
      deleteBackup,
    };
  },
  data() {
    return {
      color: "accent",
      loading: false,
      selectedBackup: {
        name: "",
        date: "",
      },
      importOptions: {},
    };
  },
  computed: {
    total(): number {
      return this.availableBackups.length || 0;
    },
  },
  methods: {
    openDialog(backup: BackupFile, event: EVENTS) {
      this.selectedBackup = backup;

      switch (event) {
        case IMPORT_EVENT:
          this.refImportDialog.open();
          break;
        case DELETE_EVENT:
          this.refDeleteConfirmation.open();
          break;
      }
    },
    async restoreBackup() {
      const payload = {
        name: this.selectedBackup.name,
        ...this.importOptions,
      };

      await this.importBackup(this.selectedBackup.name, payload);
    },
  },
});
</script>

<style scoped>
</style>