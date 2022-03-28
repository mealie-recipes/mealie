<template>
  <v-container fluid class="narrow-container">
    <BaseDialog v-model="state.storageDetails" title="Storage Details" :icon="$globals.icons.folderOutline">
      <div class="py-2">
        <template v-for="(value, key, idx) in storageDetails">
          <v-list-item :key="`item-${key}`">
            <v-list-item-title>
              <div>{{ storageDetailsText(key) }}</div>
            </v-list-item-title>
            <v-list-item-subtitle class="text-end"> {{ value }} </v-list-item-subtitle>
          </v-list-item>
          <v-divider v-if="idx != 4" :key="`divider-${key}`" class="mx-2"></v-divider>
        </template>
      </div>
    </BaseDialog>

    <BasePageTitle divider>
      <template #title> Site Maintenance </template>
    </BasePageTitle>

    <BannerExperimental />
    <div class="d-flex justify-end">
      <ButtonLink to="/admin/maintenance/logs" text="Logs" :icon="$globals.icons.file" />
    </div>

    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.wrench" title="Summary"> </BaseCardSectionTitle>
      <div class="mb-6 ml-2 d-flex" style="gap: 0.3rem">
        <BaseButton color="info" @click="getSummary">
          <template #icon> {{ $globals.icons.tools }} </template>
          Get Summary
        </BaseButton>
        <BaseButton color="info" @click="openDetails">
          <template #icon> {{ $globals.icons.folderOutline }} </template>
          Details
        </BaseButton>
      </div>
      <v-card class="ma-2" :loading="state.fetchingInfo">
        <template v-for="(value, idx) in info">
          <v-list-item :key="`item-${idx}`">
            <v-list-item-title class="py-2">
              <div>{{ value.name }}</div>
              <v-list-item-subtitle class="text-end"> {{ value.value }} </v-list-item-subtitle>
            </v-list-item-title>
          </v-list-item>
          <v-divider :key="`divider-${idx}`" class="mx-2"></v-divider>
        </template>
      </v-card>
    </section>
    <section>
      <BaseCardSectionTitle class="pb-0 mt-8" :icon="$globals.icons.wrench" title="Actions">
        Maintenance actions are <b> destructive </b> and should be used with caution. Performing any of these actions is
        <b> irreversible </b>.
      </BaseCardSectionTitle>
      <v-card class="ma-2" :loading="state.actionLoading">
        <template v-for="(action, idx) in actions">
          <v-list-item :key="`item-${idx}`" class="py-1">
            <v-list-item-title>
              <div>{{ action.name }}</div>
              <v-list-item-subtitle class="wrap-word">
                {{ action.subtitle }}
              </v-list-item-subtitle>
            </v-list-item-title>
            <BaseButton color="info" @click="action.handler">
              <template #icon> {{ $globals.icons.robot }}</template>
              Run
            </BaseButton>
          </v-list-item>
          <v-divider :key="`divider-${idx}`" class="mx-2"></v-divider>
        </template>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, ref, defineComponent, reactive } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/api";
import { MaintenanceStorageDetails, MaintenanceSummary } from "~/types/api-types/admin";

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      storageDetails: false,
      storageDetailsLoading: false,
      fetchingInfo: false,
      actionLoading: false,
    });

    const adminApi = useAdminApi();

    // ==========================================================================
    // General Info

    const infoResults = ref<MaintenanceSummary>({
      dataDirSize: "unknown",
      logFileSize: "unknown",
      cleanableDirs: 0,
      cleanableImages: 0,
    });

    async function getSummary() {
      state.fetchingInfo = true;
      const { data } = await adminApi.maintenance.getInfo();

      infoResults.value = data ?? {
        dataDirSize: "unknown",
        logFileSize: "unknown",
        cleanableDirs: 0,
        cleanableImages: 0,
      };

      state.fetchingInfo = false;
    }

    const info = computed(() => {
      return [
        {
          name: "Data Directory Size",
          value: infoResults.value.dataDirSize,
        },
        {
          name: "Log File Size",
          value: infoResults.value.logFileSize,
        },
        {
          name: "Cleanable Directories",
          value: infoResults.value.cleanableDirs,
        },
        {
          name: "Cleanable Images",
          value: infoResults.value.cleanableImages,
        },
      ];
    });

    // ==========================================================================
    // Storage Details

    const storageTitles: { [key: string]: string } = {
      tempDirSize: "Temporary Directory (.temp)",
      backupsDirSize: "Backups Directory (backups)",
      groupsDirSize: "Groups Directory (groups)",
      recipesDirSize: "Recipes Directory (recipes)",
      userDirSize: "User Directory (user)",
    };

    function storageDetailsText(key: string) {
      return storageTitles[key] ?? "unknown";
    }

    const storageDetails = ref<MaintenanceStorageDetails | null>(null);

    async function openDetails() {
      state.storageDetailsLoading = true;
      state.storageDetails = true;

      const { data } = await adminApi.maintenance.getStorageDetails();

      if (data) {
        storageDetails.value = data;
      }

      state.storageDetailsLoading = true;
    }

    // ==========================================================================
    // Actions

    async function handleDeleteLogFile() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanLogFile();
      state.actionLoading = false;
    }

    async function handleCleanDirectories() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanRecipeFolders();
      state.actionLoading = false;
    }

    async function handleCleanImages() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanImages();
      state.actionLoading = false;
    }

    async function handleCleanTemp() {
      state.actionLoading = true;
      await adminApi.maintenance.cleanTemp();
      state.actionLoading = false;
    }

    const actions = [
      {
        name: "Delete Log Files",
        handler: handleDeleteLogFile,
        subtitle: "Deletes all the log files",
      },
      {
        name: "Clean Directories",
        handler: handleCleanDirectories,
        subtitle: "Removes all the recipe folders that are not valid UUIDs",
      },
      {
        name: "Clean Temporary Files",
        handler: handleCleanTemp,
        subtitle: "Removes all files and folders in the .temp directory",
      },
      {
        name: "Clean Images",
        handler: handleCleanImages,
        subtitle: "Removes all the images that don't end with .webp",
      },
    ];

    return {
      storageDetailsText,
      openDetails,
      storageDetails,
      state,
      info,
      getSummary,
      actions,
    };
  },
  head() {
    return {
      title: this.$t("settings.site-settings") as string,
    };
  },
});
</script>

<style scoped>
.wrap-word {
  white-space: normal;
  word-wrap: break-word;
}
</style>
