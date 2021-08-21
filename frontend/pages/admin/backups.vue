// TODO: Create a new datatable below to display the import summary json files saved on server (Need to do as well).
<template>
  <v-container fluid>
    <section>
      <BaseCardSectionTitle title="Mealie Backups"> </BaseCardSectionTitle>

      <!-- Delete Dialog -->
      <BaseDialog
        ref="domDeleteConfirmation"
        :title="$t('settings.backup.delete-backup')"
        color="error"
        :icon="$globals.icons.alertCircle"
        @confirm="deleteBackup()"
      >
        <v-card-text>
          {{ $t("general.confirm-delete-generic") }}
        </v-card-text>
      </BaseDialog>

      <!-- Import Dialog -->
      <BaseDialog
        ref="domImportDialog"
        :title="selected.name"
        :icon="$globals.icons.database"
        :submit-text="$t('general.import')"
        @submit="importBackup()"
      >
        <!-- <v-card-subtitle v-if="date" class="mb-n3 mt-3"> {{ $d(new Date(date), "medium") }} </v-card-subtitle> -->
        <v-divider></v-divider>
        <v-card-text>
          <AdminBackupImportOptions v-model="selected.options" class="mt-5 mb-2" :import-backup="true" />
        </v-card-text>

        <v-divider></v-divider>
      </BaseDialog>

      <v-toolbar flat class="justify-between">
        <BaseButton class="mr-2" @click="createBackup(null)" />
        <!-- Backup Creation Dialog -->
        <BaseDialog
          :title="$t('settings.backup.create-heading')"
          :icon="$globals.icons.database"
          :submit-text="$t('general.create')"
          @submit="createBackup"
        >
          <template #activator="{ open }">
            <BaseButton secondary @click="open"> {{ $t("general.custom") }}</BaseButton>
          </template>

          <v-divider></v-divider>
          <v-card-text>
            <v-text-field v-model="backupOptions.tag" :label="$t('settings.backup.backup-tag')"> </v-text-field>
            <AdminBackupImportOptions v-model="backupOptions.options" class="mt-5 mb-2" />
            <v-divider class="my-3"></v-divider>
            <p class="text-uppercase">Templates</p>
            <v-checkbox
              v-for="(template, index) in backups.templates"
              :key="index"
              v-model="backupOptions.templates"
              :value="template"
              :label="template"
            ></v-checkbox>
          </v-card-text>
        </BaseDialog>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="backups.imports || []"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="setSelected"
      >
        <template #item.date="{ item }">
          {{ $d(Date.parse(item.date), "medium") }}
        </template>
        <template #item.actions="{ item }">
          <BaseButton
            small
            class="mx-1"
            delete
            @click.stop="
              domDeleteConfirmation.open();
              deleteTarget = item.name;
            "
          />
          <BaseButton small download :download-url="backupsFileNameDownload(item.name)" @click.stop />
        </template>
      </v-data-table>
      <v-divider></v-divider>
    </section>
  </v-container>
</template>

<script lang="ts">
import AdminBackupImportOptions from "@/components/Domain/Admin/AdminBackupImportOptions.vue";
import { defineComponent, reactive, toRefs, useContext, ref } from "@nuxtjs/composition-api";
import { useBackups } from "~/composables/use-backups";

export default defineComponent({
  components: { AdminBackupImportOptions },
  layout: "admin",
  setup() {
    const { i18n } = useContext();

    const { selected, backups, backupOptions, deleteTarget, refreshBackups, importBackup, createBackup, deleteBackup } =
      useBackups();

    const domDeleteConfirmation = ref(null);
    const domImportDialog = ref(null);
    const state = reactive({
      search: "",
      headers: [
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("general.created"), value: "date" },
        { text: "", value: "actions", align: "right" },
      ],
    });

    function setSelected(data: { name: string; date: string }) {
      if (selected.value === null || selected.value === undefined) {
        return;
      }
      selected.value.name = data.name;
      // @ts-ignore - Calling Child Method
      domImportDialog.value.open();
    }

    const backupsFileNameDownload = (fileName: string) => `api/backups/${fileName}/download`;

    return {
      selected,
      ...toRefs(state),
      backupOptions,
      backups,
      createBackup,
      deleteBackup,
      setSelected,
      deleteTarget,
      domDeleteConfirmation,
      domImportDialog,
      importBackup,
      refreshBackups,
      backupsFileNameDownload,
    };
  },
});
</script>
    
<style scoped>
</style>