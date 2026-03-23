<template>
  <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img
          width="100%"
          max-height="200"
          max-width="150"
          src="/svgs/manage-notifiers.svg"
        />
      </template>
      <template #title>
        {{ $t("settings.nextcloud-tasks") }}
      </template>
    </BasePageTitle>

    <section>
      <BaseCardSectionTitle
        class="pb-0"
        :icon="$globals.icons.cloudSync"
        :title="$t('settings.nextcloud-configuration')"
      />
      <v-card class="mb-4 pa-4">
        <v-switch
          v-model="form.nextcloudEnabled"
          :label="$t('settings.nextcloud-enable-sync')"
          color="primary"
          hide-details
        />

        <v-expand-transition>
          <div v-if="form.nextcloudEnabled">
            <v-divider class="my-4" />

            <v-text-field
              v-model="form.nextcloudUrl"
              :label="$t('settings.nextcloud-url')"
              placeholder="https://cloud.example.com"
              variant="outlined"
              density="compact"
              class="mb-2"
              :hint="$t('settings.nextcloud-url-hint')"
              persistent-hint
            />

            <v-text-field
              v-model="form.nextcloudUsername"
              :label="$t('settings.nextcloud-username')"
              variant="outlined"
              density="compact"
              class="mb-2"
            />

            <v-text-field
              v-model="form.nextcloudPassword"
              :label="$t('settings.nextcloud-password')"
              :type="showPassword ? 'text' : 'password'"
              variant="outlined"
              density="compact"
              class="mb-2"
              :hint="$t('settings.nextcloud-password-hint')"
              persistent-hint
            >
              <template #append-inner>
                <v-icon
                  :icon="showPassword ? $globals.icons.eyeOff : $globals.icons.eye"
                  style="cursor: pointer"
                  @click="showPassword = !showPassword"
                />
              </template>
            </v-text-field>

            <v-text-field
              v-model="form.nextcloudTaskList"
              :label="$t('settings.nextcloud-task-list')"
              placeholder="Tasks"
              variant="outlined"
              density="compact"
              class="mb-2"
              :hint="$t('settings.nextcloud-task-list-hint')"
              persistent-hint
            />

            <v-switch
              v-model="form.nextcloudVerifySsl"
              :label="$t('settings.nextcloud-verify-ssl')"
              color="primary"
              density="compact"
              hide-details
              class="mb-4"
            />
          </div>
        </v-expand-transition>

        <div
          class="d-flex justify-end mt-4"
          style="gap: 8px"
        >
          <BaseButton
            v-if="form.nextcloudEnabled"
            color="info"
            variant="outlined"
            :loading="testLoading"
            :disabled="!canTest"
            @click="testConnection"
          >
            <template #icon>
              {{ $globals.icons.testTube }}
            </template>
            {{ $t("general.test") }}
          </BaseButton>
          <BaseButton
            color="primary"
            variant="elevated"
            :loading="saveLoading"
            @click="savePreferences"
          >
            <template #icon>
              {{ $globals.icons.save }}
            </template>
            {{ $t("general.save") }}
          </BaseButton>
        </div>
      </v-card>
    </section>

    <section
      v-if="testResult"
      class="mt-2"
    >
      <v-alert
        :type="testResult.status === 'ok' ? 'success' : 'error'"
        variant="tonal"
        closable
        @click:close="testResult = null"
      >
        <template v-if="testResult.status === 'ok'">
          <div class="font-weight-medium mb-2">
            {{ $t("settings.nextcloud-connection-success") }}
          </div>
          <div v-if="testResult.calendars && testResult.calendars.length">
            <div class="mb-1">
              {{ $t("settings.nextcloud-available-lists") }}
            </div>
            <v-chip
              v-for="cal in testResult.calendars"
              :key="cal.slug"
              size="small"
              class="mr-1 mb-1"
              :color="isActiveList(cal) ? 'primary' : undefined"
            >
              {{ cal.display_name || cal.slug }}
              <template v-if="isActiveList(cal)">
                &nbsp;&#x2713;
              </template>
            </v-chip>
          </div>
        </template>
        <template v-else>
          {{ testResult.message || $t("settings.nextcloud-connection-failed") }}
        </template>
      </v-alert>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";

interface NextcloudTestResult {
  status: string;
  message?: string | null;
  calendars?: { slug: string; display_name: string }[] | null;
}

export default defineNuxtComponent({
  setup() {
    const api = useUserApi();
    const i18n = useI18n();

    useSeoMeta({
      title: i18n.t("settings.nextcloud-tasks"),
    });

    const form = ref({
      nextcloudEnabled: false,
      nextcloudUrl: null as string | null,
      nextcloudUsername: null as string | null,
      nextcloudPassword: null as string | null,
      nextcloudTaskList: null as string | null,
      nextcloudVerifySsl: true,
    });

    // Store full preferences for merging on save
    const fullPreferences = ref<Record<string, unknown> | null>(null);

    const showPassword = ref(false);
    const saveLoading = ref(false);
    const testLoading = ref(false);
    const testResult = ref<NextcloudTestResult | null>(null);

    const canTest = computed(() => {
      return !!(form.value.nextcloudUrl && form.value.nextcloudUsername && form.value.nextcloudPassword);
    });

    // Load current preferences directly
    onMounted(async () => {
      const { data } = await api.households.getPreferences();
      if (data) {
        fullPreferences.value = data as unknown as Record<string, unknown>;
        form.value = {
          nextcloudEnabled: (data as any).nextcloudEnabled ?? false,
          nextcloudUrl: (data as any).nextcloudUrl ?? null,
          nextcloudUsername: (data as any).nextcloudUsername ?? null,
          nextcloudPassword: (data as any).nextcloudPassword ?? null,
          nextcloudTaskList: (data as any).nextcloudTaskList ?? null,
          nextcloudVerifySsl: (data as any).nextcloudVerifySsl ?? true,
        };
      }
    });

    async function savePreferences() {
      saveLoading.value = true;
      try {
        // Merge form values into full preferences
        const payload = {
          ...(fullPreferences.value || {}),
          ...form.value,
        };
        // Remove 'id' if present (read-only field)
        delete (payload as any).id;
        const { data } = await api.households.setPreferences(payload as any);
        if (data) {
          fullPreferences.value = data as unknown as Record<string, unknown>;
        }
      }
      finally {
        saveLoading.value = false;
      }
    }

    async function testConnection() {
      testLoading.value = true;
      testResult.value = null;
      try {
        // Save first so the test uses the latest credentials
        await savePreferences();
        const { data } = await api.households.testNextcloud();
        if (data) {
          testResult.value = data;
        }
      }
      finally {
        testLoading.value = false;
      }
    }

    function isActiveList(cal: { slug: string; display_name: string }) {
      const tl = form.value.nextcloudTaskList;
      return tl && (cal.display_name === tl || cal.slug === tl);
    }

    return {
      form,
      showPassword,
      saveLoading,
      testLoading,
      testResult,
      canTest,
      savePreferences,
      testConnection,
      isActiveList,
    };
  },
});
</script>
