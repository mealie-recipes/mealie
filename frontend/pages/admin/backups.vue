<template>
  <v-container fluid>
    <BannerExperimental issue="https://github.com/hay-kot/mealie/issues/871"></BannerExperimental>
    <section>
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
      <BaseDialog v-model="importDialog" color="error" title="Backup Restore" :icon="$globals.icons.database">
        <v-divider></v-divider>
        <v-card-text>
          Restoring this backup will overwrite all the current data in your database and in the data directory and
          replace them with the contents of this backup. <b> This action cannot be undone - use with caution. </b> If
          the restoration is successful, you will be logged out.

          <v-checkbox
            v-model="confirmImport"
            class="checkbox-top"
            color="error"
            hide-details
            label="I understand that this action is irreversible, destructive and may cause data loss"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions class="justify-center pt-0">
          <BaseButton delete :disabled="!confirmImport" @click="restoreBackup(selected)">
            <template #icon> {{ $globals.icons.database }} </template>
            Restore Backup
          </BaseButton>
        </v-card-actions>
        <p class="caption pb-0 mb-1 text-center">
          {{ selected.name }}
        </p>
      </BaseDialog>

      <section>
        <BaseCardSectionTitle title="Backups">
          <v-card-text class="py-0 px-1">
            Backups a total snapshots of the database and data directory of the site. This includes all data and cannot
            be set to exclude subsets of data. You can think off this as a snapshot of Mealie at a specific time.
            Currently, this backup mechanism is not cross-version and therefore cannot be used to migrate data between
            versions (data migrations are not done automatically). These serve as a database agnostic way to export and
            import data or backup the site to an external location.
          </v-card-text>
        </BaseCardSectionTitle>
        <BaseButton @click="createBackup"> {{ $t("settings.backup.create-heading") }} </BaseButton>

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
              url="/api/admin/backups/upload"
              accept=".zip"
              color="info"
              @uploaded="refreshBackups()"
            />
          </div>
        </div>
      </section>
    </section>
    <v-container class="mt-4 d-flex justify-end">
      <v-btn outlined rounded to="/user/group/data/migrations"> Looking For Migrations? </v-btn>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { onMounted } from "vue-demi";
import { useAdminApi } from "~/composables/api";
import { AllBackups } from "~/types/api-types/admin";

export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n, $auth } = useContext();

    const adminApi = useAdminApi();
    const selected = ref("");

    const backups = ref<AllBackups>({
      imports: [],
      templates: [],
    });

    async function refreshBackups() {
      const { data } = await adminApi.backups.getAll();
      if (data) {
        backups.value = data;
      }
    }

    async function createBackup() {
      const { data } = await adminApi.backups.create();

      if (!data?.error) {
        refreshBackups();
      }
    }

    async function restoreBackup(fileName: string) {
      const { data } = await adminApi.backups.restore(fileName);

      if (!data?.error) {
        $auth.logout();
      }
    }

    const deleteTarget = ref("");

    async function deleteBackup() {
      const { data } = await adminApi.backups.delete(deleteTarget.value);

      if (!data?.error) {
        refreshBackups();
      }
    }

    const state = reactive({
      confirmImport: false,
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
      selected.value = data.name;
      state.importDialog = true;
    }

    const backupsFileNameDownload = (fileName: string) => `api/admin/backups/${fileName}`;

    onMounted(refreshBackups);

    return {
      restoreBackup,
      selected,
      ...toRefs(state),
      backups,
      createBackup,
      deleteBackup,
      deleteTarget,
      setSelected,
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

<style>
.v-input--selection-controls__input {
  margin-bottom: auto;
}
</style>
