<template>
  <v-container
    fluid
    class="narrow-container"
  >
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="150"
          src="/svgs/admin-site-settings.svg"
        />
      </template>
      <template #title>
        {{ $t("settings.nextcloud-tasks") }}
      </template>
    </BasePageTitle>

    <!-- Configuration Status -->
    <section>
      <BaseCardSectionTitle
        class="pb-0"
        :icon="$globals.icons.cloudSync"
        :title="$t('settings.nextcloud-configuration')"
      />
      <v-alert
        border="start"
        :border-color="config.enabled ? 'success' : 'warning'"
        variant="text"
        elevation="2"
      >
        <template #prepend>
          <v-icon :color="config.enabled ? 'success' : 'warning'">
            {{ config.enabled ? $globals.icons.checkboxMarkedCircle : $globals.icons.alertCircle }}
          </v-icon>
        </template>
        <div class="font-weight-medium">
          {{ $t("settings.nextcloud-configuration-status") }}
        </div>
        <div>
          {{ config.enabled ? $t("settings.ready") : $t("settings.nextcloud-not-configured") }}
        </div>
      </v-alert>
    </section>

    <!-- Current Configuration -->
    <section
      v-if="config.enabled"
      class="mt-4"
    >
      <BaseCardSectionTitle
        class="pb-0"
        :icon="$globals.icons.cog"
        :title="$t('settings.configuration')"
      />
      <v-card class="mb-4">
        <v-list-item :title="$t('settings.nextcloud-url')">
          <template #prepend>
            <v-icon class="opacity-100">
              {{ $globals.icons.link }}
            </v-icon>
          </template>
          <v-list-item-subtitle>{{ config.url || "-" }}</v-list-item-subtitle>
        </v-list-item>
        <v-divider />
        <v-list-item :title="$t('settings.nextcloud-username')">
          <template #prepend>
            <v-icon class="opacity-100">
              {{ $globals.icons.user }}
            </v-icon>
          </template>
          <v-list-item-subtitle>{{ config.username || "-" }}</v-list-item-subtitle>
        </v-list-item>
        <v-divider />
        <v-list-item :title="$t('settings.nextcloud-task-list')">
          <template #prepend>
            <v-icon class="opacity-100">
              {{ $globals.icons.cartCheck }}
            </v-icon>
          </template>
          <v-list-item-subtitle>{{ config.taskList || "-" }}</v-list-item-subtitle>
        </v-list-item>
      </v-card>
    </section>

    <!-- Environment Variable Instructions -->
    <section
      v-if="!config.enabled"
      class="mt-4"
    >
      <BaseCardSectionTitle
        class="pb-0"
        :icon="$globals.icons.information"
        :title="$t('settings.nextcloud-setup')"
      />
      <v-card class="mb-4 pa-4">
        <p class="mb-3">
          {{ $t("settings.nextcloud-setup-description") }}
        </p>
        <v-code class="d-block pa-3">
          NEXTCLOUD_URL=https://cloud.example.com
          <br>NEXTCLOUD_USERNAME=your_user
          <br>NEXTCLOUD_PASSWORD=your_app_password
          <br>NEXTCLOUD_TASK_LIST=Tasks
          <br>NEXTCLOUD_VERIFY_SSL=true
        </v-code>
      </v-card>
    </section>

    <!-- Test Connection -->
    <section
      v-if="config.enabled"
      class="mt-4"
    >
      <BaseCardSectionTitle
        class="pb-0"
        :icon="$globals.icons.testTube"
        :title="$t('settings.nextcloud-test-connection')"
      />
      <v-card class="mb-4 pa-4">
        <BaseButton
          color="info"
          variant="elevated"
          :loading="testLoading"
          @click="testConnection"
        >
          <template #icon>
            {{ $globals.icons.cloudSync }}
          </template>
          {{ $t("general.test") }}
        </BaseButton>

        <template v-if="testResult">
          <v-divider class="my-4" />
          <v-alert
            :type="testResult.status === 'ok' ? 'success' : 'error'"
            variant="tonal"
          >
            <template v-if="testResult.status === 'ok'">
              <div class="font-weight-medium mb-2">
                {{ $t("settings.nextcloud-connection-success") }}
              </div>
              <div v-if="testResult.calendars && testResult.calendars.length">
                <div class="font-weight-medium mb-1">
                  {{ $t("settings.nextcloud-available-lists") }}
                </div>
                <v-chip
                  v-for="cal in testResult.calendars"
                  :key="cal.slug"
                  size="small"
                  class="mr-1 mb-1"
                  :color="cal.display_name === config.taskList || cal.slug === config.taskList ? 'primary' : undefined"
                >
                  {{ cal.display_name || cal.slug }}
                </v-chip>
              </div>
            </template>
            <template v-else>
              {{ testResult.message || $t("settings.nextcloud-connection-failed") }}
            </template>
          </v-alert>
        </template>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi } from "~/composables/api";
import type { NextcloudConfigResponse, NextcloudTestResponse } from "~/lib/api/admin/admin-nextcloud";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "admin",
    });

    onMounted(() => {
      setPageLayout("admin");
    });

    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("settings.nextcloud-tasks"),
    });

    const adminApi = useAdminApi();

    const config = ref<NextcloudConfigResponse>({
      enabled: false,
      url: null,
      username: null,
      taskList: null,
    });

    const testLoading = ref(false);
    const testResult = ref<NextcloudTestResponse | null>(null);

    onMounted(async () => {
      const { data } = await adminApi.nextcloud.getConfig();
      if (data) {
        config.value = data;
      }
    });

    async function testConnection() {
      testLoading.value = true;
      testResult.value = null;
      const { data } = await adminApi.nextcloud.testConnection();
      if (data) {
        testResult.value = data;
      }
      testLoading.value = false;
    }

    return {
      config,
      testLoading,
      testResult,
      testConnection,
    };
  },
});
</script>
