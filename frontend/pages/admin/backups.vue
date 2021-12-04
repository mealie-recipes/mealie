// TODO: Create a new datatable below to display the import summary json files saved on server (Need to do as well).
<template>
  <v-container fluid>
    <section>
      <BaseCardSectionTitle title="Site Backups"> </BaseCardSectionTitle>

      <!-- Delete Dialog -->
      <BaseDialog
        v-model="deleteDialog"
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
        v-model="importDialog"
        :title="selected.name"
        :icon="$globals.icons.database"
        :submit-text="$t('general.import')"
        @submit="importBackup()"
      >
        <v-divider></v-divider>
        <v-card-text>
          <AdminBackupImportOptions v-model="selected.options" class="mt-5 mb-2" :import-backup="true" />
        </v-card-text>

        <v-divider></v-divider>
      </BaseDialog>

      <v-card outlined>
        <v-card-title class="py-2"> {{ $t("settings.backup.create-heading") }} </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-form @submit.prevent="createBackup()">
          <v-card-text>
            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Dolores molestiae alias incidunt fugiat!
            Recusandae natus numquam iusto voluptates deserunt quia? Sed voluptate rem facilis tempora, perspiciatis
            corrupti dolore obcaecati laudantium!
            <div style="max-width: 300px">
              <v-text-field
                v-model="backupOptions.tag"
                class="mt-4"
                :label="$t('settings.backup.backup-tag') + ' (optional)'"
              >
              </v-text-field>
              <AdminBackupImportOptions v-model="backupOptions.options" class="mt-5 mb-2" />
              <v-divider class="my-3"></v-divider>
            </div>
            <v-card-actions>
              <BaseButton type="submit"> </BaseButton>
            </v-card-actions>
          </v-card-text>
        </v-form>
      </v-card>

      <section class="mt-5">
        <BaseCardSectionTitle title="Backups"></BaseCardSectionTitle>
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
            <v-btn
              icon
              class="mx-1"
              color="error"
              @click.stop="
                deleteDialog = true;
                deleteTarget = item.name;
              "
            >
              <v-icon> {{ $globals.icons.delete }} </v-icon>
            </v-btn>
            <BaseButton small download :download-url="backupsFileNameDownload(item.name)" @click.stop />
          </template>
        </v-data-table>
        <v-divider></v-divider>
        <div class="d-flex justify-end mt-6">
          <div>
            <AppButtonUpload
              :text-btn="false"
              class="mr-4"
              url="/api/backups/upload"
              accept=".zip"
              color="info"
              @uploaded="refreshBackups()"
            />
          </div>
        </div>
      </section>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext } from "@nuxtjs/composition-api";
import AdminBackupImportOptions from "@/components/Domain/Admin/AdminBackupImportOptions.vue";
import { useBackups } from "~/composables/use-backups";

export default defineComponent({
  components: { AdminBackupImportOptions },
  layout: "admin",
  setup() {
    const { i18n } = useContext();

    const { selected, backups, backupOptions, deleteTarget, refreshBackups, importBackup, createBackup, deleteBackup } =
      useBackups();

    const state = reactive({
      deleteDialog: false,
      createDialog: false,
      importDialog: false,
      search: "",
      headers: [
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("general.created"), value: "date" },
        { text: "Size", value: "size" },
        { text: "", value: "actions", align: "right" },
      ],
    });

    function setSelected(data: { name: string; date: string }) {
      if (selected.value === null || selected.value === undefined) {
        return;
      }
      selected.value.name = data.name;
      state.importDialog = true;
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
      importBackup,
      refreshBackups,
      backupsFileNameDownload,
    };
  },
  head() {
    return {
      title: this.$t("sidebar.backups") as string,
    };
  },
});
</script>
    
<style scoped>
</style>