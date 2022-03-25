<template>
  <v-container fluid class="narrow-container">
    <BasePageTitle divider>
      <template #title> Site Maintenance </template>
    </BasePageTitle>

    <BannerExperimental />

    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.cog" title="Summary"> </BaseCardSectionTitle>
      <div class="mb-6 ml-2">
        <BaseButton color="info" @click="getSummary">
          <template #icon> {{ $globals.icons.tools }} </template>
          Get Summary
        </BaseButton>
      </div>
      <v-card class="ma-2" :loading="state.fetchingInfo">
        <template v-for="(value, idx) in info">
          <v-list-item :key="`item-${idx}`">
            <v-list-item-title>
              <div>{{ value.name }}</div>
            </v-list-item-title>
            <v-list-item-subtitle class="text-end"> {{ value.value }} </v-list-item-subtitle>
          </v-list-item>
          <v-divider :key="`divider-${idx}`" class="mx-2"></v-divider>
        </template>
      </v-card>
    </section>
    <section>
      <BaseCardSectionTitle class="pb-0 mt-8" :icon="$globals.icons.cog" title="Actions">
        Maintenance actions are <b> destructive </b> and should be used with caution. Performing any of these actions is
        <b> irreversible </b>.
      </BaseCardSectionTitle>
      <v-card class="ma-2" :loading="state.actionLoading">
        <template v-for="(action, idx) in actions">
          <v-list-item :key="`item-${idx}`">
            <v-list-item-title>
              <div>{{ action.name }}</div>
              <v-list-item-subtitle>
                {{ action.subtitle }}
              </v-list-item-subtitle>
            </v-list-item-title>
            <v-list-item-action>
              <BaseButton color="info" @click="action.handler">
                <template #icon> {{ $globals.icons.robot }}</template>
                Run
              </BaseButton>
            </v-list-item-action>
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
import { MaintenanceSummary } from "~/types/api-types/admin";

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      fetchingInfo: false,
      actionLoading: false,
    });

    const adminApi = useAdminApi();

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
        name: "Clean Images",
        handler: handleCleanImages,
        subtitle: "Removes all the images that don't end with .webp",
      },
    ];

    return {
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

<style scoped></style>
