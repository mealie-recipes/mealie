<template>
  <v-container
    v-if="household"
    class="narrow-container"
  >
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
          v-model="household.preferences.nextcloudEnabled"
          :label="$t('settings.nextcloud-enable-sync')"
          color="primary"
          hide-details
        />

        <v-expand-transition>
          <div v-if="household.preferences.nextcloudEnabled">
            <v-divider class="my-4" />

            <v-text-field
              v-model="household.preferences.nextcloudUrl"
              :label="$t('settings.nextcloud-url')"
              placeholder="https://cloud.example.com"
              variant="outlined"
              density="compact"
              class="mb-2"
              :hint="$t('settings.nextcloud-url-hint')"
              persistent-hint
            />

            <v-text-field
              v-model="household.preferences.nextcloudUsername"
              :label="$t('settings.nextcloud-username')"
              variant="outlined"
              density="compact"
              class="mb-2"
            />

            <v-text-field
              v-model="household.preferences.nextcloudPassword"
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

            <v-switch
              v-model="household.preferences.nextcloudVerifySsl"
              :label="$t('settings.nextcloud-verify-ssl')"
              color="primary"
              density="compact"
              hide-details
              class="mb-4"
            />

            <div class="d-flex justify-end mb-4">
              <BaseButton
                color="info"
                variant="outlined"
                :loading="testLoading"
                :disabled="!canTest"
                @click="handleTest"
              >
                <template #icon>
                  {{ $globals.icons.testTube }}
                </template>
                {{ $t("settings.nextcloud-test-connection") }}
              </BaseButton>
            </div>

            <v-expand-transition>
              <v-alert
                v-if="testResult && testResult.status !== 'ok'"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="testResult = null"
              >
                {{ testResult.message || $t("settings.nextcloud-connection-failed") }}
              </v-alert>
            </v-expand-transition>

            <v-combobox
              v-model="household.preferences.nextcloudTaskList"
              :items="availableLists"
              item-title="label"
              item-value="value"
              :return-object="false"
              :label="$t('settings.nextcloud-task-list')"
              placeholder="Tasks"
              variant="outlined"
              density="compact"
              class="mb-2"
              :hint="availableLists.length ? $t('settings.nextcloud-task-list-hint-tested') : $t('settings.nextcloud-task-list-hint')"
              persistent-hint
            >
              <template #item="{ item, props: itemProps }">
                <v-list-item v-bind="itemProps">
                  <template #append>
                    <v-icon
                      v-if="isActiveList(item.raw)"
                      color="primary"
                      size="small"
                    >
                      {{ $globals.icons.check }}
                    </v-icon>
                  </template>
                </v-list-item>
              </template>
            </v-combobox>
          </div>
        </v-expand-transition>

        <div
          class="d-flex justify-end mt-4"
          style="gap: 8px"
        >
          <BaseButton
            color="primary"
            variant="elevated"
            :loading="saveLoading"
            @click="handleSave"
          >
            <template #icon>
              {{ $globals.icons.save }}
            </template>
            {{ $t("general.save") }}
          </BaseButton>
        </div>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";

interface NextcloudTestResult {
  status: string;
  message?: string | null;
  calendars?: { slug: string; display_name: string }[] | null;
}

interface ListOption {
  label: string;
  value: string;
}

export default defineNuxtComponent({
  middleware: ["can-manage-household-only"],
  setup() {
    const api = useUserApi();
    const i18n = useI18n();
    const { household, actions: householdActions } = useHouseholdSelf();

    useSeoMeta({
      title: i18n.t("settings.nextcloud-tasks"),
    });

    const showPassword = ref(false);
    const saveLoading = ref(false);
    const testLoading = ref(false);
    const testResult = ref<NextcloudTestResult | null>(null);
    const availableLists = ref<ListOption[]>([]);

    const canTest = computed(() => {
      const p = household.value?.preferences;
      return !!(p?.nextcloudUrl && p?.nextcloudUsername && p?.nextcloudPassword);
    });

    async function handleSave() {
      saveLoading.value = true;
      const data = await householdActions.updatePreferences();
      if (data) {
        alert.success(i18n.t("settings.settings-updated"));
      }
      else {
        alert.error(i18n.t("settings.settings-update-failed"));
      }
      saveLoading.value = false;
    }

    async function handleTest() {
      testLoading.value = true;
      testResult.value = null;
      availableLists.value = [];
      // Save first so the backend has the latest credentials
      await handleSave();
      const { data } = await api.households.testNextcloud();
      if (data) {
        testResult.value = data;
        if (data.status === "ok" && data.calendars) {
          // Populate combobox with discovered lists
          availableLists.value = data.calendars
            .filter((c: any) => c.display_name || c.slug)
            .map((c: any) => ({
              label: c.display_name || c.slug,
              value: c.display_name || c.slug,
            }));
          alert.success(i18n.t("settings.nextcloud-connection-success"));
        }
      }
      testLoading.value = false;
    }

    function isActiveList(item: ListOption) {
      const tl = household.value?.preferences?.nextcloudTaskList;
      return tl && item.value === tl;
    }

    return {
      household,
      showPassword,
      saveLoading,
      testLoading,
      testResult,
      availableLists,
      canTest,
      handleSave,
      handleTest,
      isActiveList,
    };
  },
});
</script>
