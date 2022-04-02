<template>
  <v-container fluid class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200" max-width="150" :src="require('~/static/svgs/admin-site-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t("settings.site-settings") }} </template>
    </BasePageTitle>

    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.cog" title="Configuration"> </BaseCardSectionTitle>
      <v-card class="mb-4">
        <template v-for="(check, idx) in simpleChecks">
          <v-list-item :key="`list-item-${idx}`">
            <v-list-item-icon>
              <v-icon :color="getColor(check.status, check.warning)">
                {{ getIcon(check.status, check.warning) }}
              </v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>
                {{ check.text }}
              </v-list-item-title>
              <v-list-item-subtitle class="wrap-word">
                {{ check.status ? check.successText : check.errorText }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-divider :key="`divider-${idx}`"></v-divider>
        </template>
      </v-card>
    </section>

    <section>
      <BaseCardSectionTitle class="pt-2" :icon="$globals.icons.docker" title="Docker Volumes" />
      <v-alert
        border="left"
        colored-border
        :type="docker.state === DockerVolumeState.Error ? 'error' : 'info'"
        :icon="$globals.icons.docker"
        elevation="2"
        :loading="docker.loading"
      >
        <div class="d-flex align-center font-weight-medium">
          Docker Volume Tests
          <HelpIcon small class="my-n3">
            Mealie requires that the frontend container and the backend share the same docker volume or storage. This
            ensures that the frontend container can properly access the images and assets stored on disk.
          </HelpIcon>
        </div>
        <div>
          <template v-if="docker.state === DockerVolumeState.Error"> Volumes are misconfigured </template>
          <template v-else-if="docker.state === DockerVolumeState.Success">
            Volume status was successfully validated
          </template>
          <template v-else-if="docker.state === DockerVolumeState.Unknown">
            Status Unknown. Try running a validation.
          </template>
        </div>
        <div class="mt-4">
          <BaseButton color="info" :loading="docker.loading" @click="dockerValidate">
            <template #icon> {{ $globals.icons.checkboxMarkedCircle }} </template>
            Validate
          </BaseButton>
        </div>
      </v-alert>
    </section>

    <section>
      <BaseCardSectionTitle class="pt-2" :icon="$globals.icons.email" title="Email" />
      <v-alert border="left" colored-border :type="getColor(appConfig.emailReady)" elevation="2">
        <div class="font-weight-medium">Email Configuration Status</div>
        <div>
          {{ appConfig.emailReady ? "Ready" : "Not Ready - Check Environmental Variables" }}
        </div>
        <div>
          <v-text-field v-model="address" class="mr-4" :label="$t('user.email')" :rules="[validators.email]">
          </v-text-field>
          <BaseButton
            color="info"
            :disabled="!appConfig.emailReady || !validEmail"
            :loading="loading"
            @click="testEmail"
          >
            <template #icon> {{ $globals.icons.email }} </template>
            {{ $t("general.test") }}
          </BaseButton>
          <template v-if="tested">
            <v-divider class="my-x mt-6"></v-divider>
            <v-card-text class="px-0">
              <h4>Email Test Results</h4>
              <span class="pl-4">
                {{ success ? "Succeeded" : "Failed" }}
              </span>
            </v-card-text>
          </template>
        </div>
      </v-alert>
    </section>
    <section class="mt-4">
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.cog" title="General About"> </BaseCardSectionTitle>
      <v-card class="mb-4">
        <v-list-item v-for="property in appInfo" :key="property.name">
          <v-list-item-icon>
            <v-icon> {{ property.icon || $globals.icons.user }} </v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>
              <div>{{ property.name }}</div>
            </v-list-item-title>
            <v-list-item-subtitle class="text-end">
              {{ property.value }}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-card>
    </section>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  onMounted,
  reactive,
  toRefs,
  ref,
  defineComponent,
  useAsync,
  useContext,
} from "@nuxtjs/composition-api";
import { useAdminApi, useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { useAsyncKey } from "~/composables/use-utils";
import { CheckAppConfig } from "~/types/api-types/admin";

enum DockerVolumeState {
  Unknown = "unknown",
  Success = "success",
  Error = "error",
}

interface SimpleCheck {
  status: boolean;
  text: string;
  successText: string;
  errorText: string;
  warning: boolean;
}

interface CheckApp extends CheckAppConfig {
  isSiteSecure?: boolean;
}

export default defineComponent({
  layout: "admin",
  setup() {
    // ==========================================================
    // Docker Volume Validation
    const docker = reactive({
      loading: false,
      state: DockerVolumeState.Unknown,
    });

    async function dockerValidate() {
      docker.loading = true;

      // Do API Check
      const { data } = await adminApi.about.checkDocker();
      if (data == null) {
        docker.state = DockerVolumeState.Error;
        return;
      }

      // Get File Contents
      const { data: fileContents } = await adminApi.about.getDockerValidateFileContents();

      if (data.text === fileContents) {
        docker.state = DockerVolumeState.Success;
      } else {
        docker.state = DockerVolumeState.Error;
      }

      docker.loading = false;
    }

    const state = reactive({
      loading: false,
      address: "",
      success: false,
      error: "",
      tested: false,
    });

    const appConfig = ref<CheckApp>({
      emailReady: true,
      baseUrlSet: true,
      isSiteSecure: true,
      isUpToDate: false,
      ldapReady: false,
    });

    const api = useUserApi();
    const adminApi = useAdminApi();

    onMounted(async () => {
      const { data } = await adminApi.about.checkApp();

      if (data) {
        appConfig.value = data;
      }

      appConfig.value.isSiteSecure = isLocalHostOrHttps();
    });

    function isLocalHostOrHttps() {
      return window.location.hostname === "localhost" || window.location.protocol === "https:";
    }

    function getColor(booly: unknown, warning = false) {
      const falsey = warning ? "warning" : "error";
      return booly ? "success" : falsey;
    }

    function getIcon(booly: unknown, warning = false) {
      if (booly === true) {
        return $globals.icons.checkboxMarkedCircle;
      } else if (warning === false) {
        return $globals.icons.alert;
      }
      return $globals.icons.alertCircle;
    }

    // @ts-ignore adfadsf
    const simpleChecks = computed<SimpleCheck[]>(() => {
      return [
        {
          status: appConfig.value.isUpToDate,
          text: "Application Version",
          errorText: `Your current version (${rawAppInfo.value.version}) does not match the latest release. Considering updating to the latest version (${rawAppInfo.value.versionLatest}).`,
          successText: "Mealie is up to date",
          warning: true,
        },
        {
          status: appConfig.value.isSiteSecure,
          text: "Secure Site",
          errorText: "Serve via localhost or secure with https. Clipboard and additional browser APIs may not work.",
          successText: "Site is accessed by localhost or https",
          warning: false,
        },
        {
          status: appConfig.value.baseUrlSet,
          text: "Server Side Base URL",
          errorText:
            "`BASE_URL` is still the default value on API Server. This will cause issues with notifications links generated on the server for emails, etc.",
          successText: "Server Side URL does not match the default",
          warning: false,
        },
        {
          status: appConfig.value.ldapReady,
          text: "LDAP Ready",
          errorText:
            "Not all LDAP Values are configured. This can be ignored if you are not using LDAP Authentication.",
          successText: "Required LDAP variables are all set.",
          warning: true,
        },
      ];
    });

    async function testEmail() {
      state.loading = true;
      state.tested = false;
      const { data } = await api.email.test({ email: state.address });

      if (data) {
        if (data.success) {
          state.success = true;
        } else {
          state.error = data.error;
          state.success = false;
        }
      }
      state.loading = false;
      state.tested = true;
    }

    const validEmail = computed(() => {
      if (state.address === "") {
        return false;
      }
      const valid = validators.email(state.address);

      // Explicit bool check because validators.email sometimes returns a string
      if (valid === true) {
        return true;
      }
      return false;
    });

    // ============================================================
    // General About Info

    const { $globals, i18n } = useContext();

    const rawAppInfo = ref({
      version: "null",
      versionLatest: "null",
    });

    function getAppInfo() {
      const statistics = useAsync(async () => {
        const { data } = await adminApi.about.about();

        if (data) {
          rawAppInfo.value.version = data.version;
          rawAppInfo.value.versionLatest = data.versionLatest;

          const prettyInfo = [
            {
              name: i18n.t("about.version"),
              icon: $globals.icons.information,
              value: data.version,
            },
            {
              name: "Build",
              icon: $globals.icons.information,
              value: data.buildId,
            },
            {
              name: i18n.t("about.application-mode"),
              icon: $globals.icons.devTo,
              value: data.production ? i18n.t("about.production") : i18n.t("about.development"),
            },
            {
              name: i18n.t("about.demo-status"),
              icon: $globals.icons.testTube,
              value: data.demoStatus ? i18n.t("about.demo") : i18n.t("about.not-demo"),
            },
            {
              name: i18n.t("about.api-port"),
              icon: $globals.icons.api,
              value: data.apiPort,
            },
            {
              name: i18n.t("about.api-docs"),
              icon: $globals.icons.file,
              value: data.apiDocs ? i18n.t("general.enabled") : i18n.t("general.disabled"),
            },
            {
              name: i18n.t("about.database-type"),
              icon: $globals.icons.database,
              value: data.dbType,
            },
            {
              name: i18n.t("about.database-url"),
              icon: $globals.icons.database,
              value: data.dbUrl,
            },
            {
              name: i18n.t("about.default-group"),
              icon: $globals.icons.group,
              value: data.defaultGroup,
            },
          ];

          return prettyInfo;
        }

        return data;
      }, useAsyncKey());

      return statistics;
    }

    const appInfo = getAppInfo();

    return {
      DockerVolumeState,
      docker,
      dockerValidate,
      simpleChecks,
      getColor,
      getIcon,
      appConfig,
      validEmail,
      validators,
      ...toRefs(state),
      testEmail,
      appInfo,
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
