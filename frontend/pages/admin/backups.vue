<template>
  <v-container fluid>
    <section>
      <!-- Delete Dialog -->
      <BaseDialog
        v-model="deleteDialog"
        :title="$tc('settings.backup.delete-backup')"
        color="error"
        :icon="$globals.icons.alertCircle"
        @confirm="deleteBackup()"
      >
        <v-card-text>
          {{ $t("general.confirm-delete-generic") }}
        </v-card-text>
      </BaseDialog>

      <!-- Import Dialog -->
      <BaseDialog v-model="importDialog" color="error" :title="$t('settings.backup.backup-restore')" :icon="$globals.icons.database">
        <v-divider></v-divider>
        <v-card-text>
          <i18n path="settings.backup.back-restore-description">
            <template #cannot-be-undone>
              <b> {{ $t('settings.backup.cannot-be-undone') }} </b>
            </template>
          </i18n>

          <p class="mt-3">
            <i18n path="settings.backup.postgresql-note">
              <template #backup-restore-process>
                <a href="https://nightly.mealie.io/documentation/getting-started/usage/backups-and-restoring/" >{{ $t('settings.backup.backup-restore-process-in-the-documentation') }}</a >
              </template>
            </i18n>
            {{ $t('') }}
          </p>


          <v-checkbox
            v-model="confirmImport"
            class="checkbox-top"
            color="error"
            hide-details
            :label="$t('settings.backup.irreversible-acknowledgment')"
          ></v-checkbox>
        </v-card-text>
        <v-card-actions class="justify-center pt-0">
          <BaseButton delete :disabled="!confirmImport || runningRestore" @click="restoreBackup(selected)">
            <template #icon> {{ $globals.icons.database }} </template>
            {{ $t('settings.backup.restore-backup') }}
          </BaseButton>
        </v-card-actions>
        <p class="caption pb-0 mb-1 text-center">
          {{ selected }}
        </p>
        <v-progress-linear v-if="runningRestore" indeterminate></v-progress-linear>
      </BaseDialog>

      <section>
        <BaseCardSectionTitle :title="$tc('settings.backup-and-exports')">
          <v-card-text class="py-0 px-1">
          <i18n path="settings.backup.experimental-description" />
          </v-card-text>
        </BaseCardSectionTitle>
        <v-toolbar color="transparent" flat class="justify-between">
        <BaseButton class="mr-2" @click="createBackup"> {{ $t("settings.backup.create-heading") }} </BaseButton>
        <AppButtonUpload
                :text-btn="false"
                url="/api/admin/backups/upload"
                accept=".zip"
                color="info"
                @uploaded="refreshBackups()"
              />
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
            <BaseButton small download :download-url="backupsFileNameDownload(item.name)" class="mx-1" @click.stop="() => {}"/>
            <BaseButton small @click.stop="setSelected(item); importDialog = true">
              <template #icon> {{ $globals.icons.backupRestore }}</template>
              {{ $t("settings.backup.backup-restore") }}
          </BaseButton>
          </template>
        </v-data-table>
        <v-divider></v-divider>
        <div class="d-flex justify-end mt-6">
          <div>

          </div>
        </div>
      </section>
    </section>
    <v-container class="mt-4 d-flex justify-center text-center">
      <nuxt-link :to="`/group/migrations`"> {{ $t('recipe.looking-for-migrations') }} </nuxt-link>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, useContext, onMounted, useRoute } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { AllBackups } from "~/lib/api/types/admin";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n, $auth } = useContext();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

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

      if (data?.error === false) {
        refreshBackups();
        alert.success(i18n.tc("settings.backup.backup-created"));
      } else {
        alert.error(i18n.tc("settings.backup.error-creating-backup-see-log-file"));
      }
    }

    async function restoreBackup(fileName: string) {
      state.runningRestore = true;
      const { error } = await adminApi.backups.restore(fileName);

      if (error) {
        console.log(error);
        state.importDialog = false;
        state.runningRestore = false;
        alert.error(i18n.tc("settings.backup.restore-fail"));
      } else {
        alert.success(i18n.tc("settings.backup.restore-success"));
        $auth.logout();
      }
    }

    const deleteTarget = ref("");

    async function deleteBackup() {
      const { data } = await adminApi.backups.delete(deleteTarget.value);

      if (!data?.error) {
        alert.success(i18n.tc("settings.backup.backup-deleted"));
        refreshBackups();
      }
    }

    const state = reactive({
      confirmImport: false,
      deleteDialog: false,
      createDialog: false,
      importDialog: false,
      runningRestore: false,
      search: "",
      headers: [
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("general.created"), value: "date" },
        { text: i18n.t("export.size"), value: "size" },
        { text: "", value: "actions", align: "right" },
      ],
    });

    function setSelected(data: { name: string; date: string }) {
      if (selected.value === null || selected.value === undefined) {
        return;
      }
      selected.value = data.name;
    }

    const backupsFileNameDownload = (fileName: string) => `api/admin/backups/${fileName}`;

    onMounted(refreshBackups);

    return {
      groupSlug,
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
