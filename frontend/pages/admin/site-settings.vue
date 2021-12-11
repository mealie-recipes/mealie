<template>
  <v-container fluid class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="200" max-width="150" :src="require('~/static/svgs/admin-site-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t("settings.site-settings") }} </template>
    </BasePageTitle>

    <section>
      <BaseCardSectionTitle class="pb-0" :icon="$globals.icons.cog" title="General Configuration">
      </BaseCardSectionTitle>

      <v-alert
        v-for="(check, idx) in simpleChecks"
        :key="idx"
        border="left"
        colored-border
        :type="getColor(check.status, check.warning)"
        elevation="2"
      >
        <div class="font-weight-medium">{{ check.text }}</div>
        <div>
          {{ check.status ? check.successText : check.errorText }}
        </div>
      </v-alert>
    </section>
    <section>
      <BaseCardSectionTitle class="pt-2" :icon="$globals.icons.email" title="Email Configuration" />
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
            <v-divider class="my-x"></v-divider>
            <v-card-text>
              Email Test Result: {{ success ? "Succeeded" : "Failed" }}
              <div>Errors: {{ error }}</div>
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
import { AdminAboutInfo, CheckAppConfig } from "~/api/admin/admin-about";
import { useAdminApi, useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { useAsyncKey } from "~/composables/use-utils";

interface SimpleCheck {
  status: boolean;
  text: string;
  successText: string;
  errorText: string;
}

export default defineComponent({
  layout: "admin",
  setup() {
    const state = reactive({
      loading: false,
      address: "",
      success: false,
      error: "",
      tested: false,
    });

    const appConfig = ref<CheckAppConfig>({
      emailReady: false,
      baseUrlSet: false,
      isSiteSecure: false,
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

    function getColor(booly: boolean | any, warning = false) {
      const falsey = warning ? "warning" : "error";
      return booly ? "success" : falsey;
    }

    // ============================================================
    // General About Info

    // @ts-ignore
    const { $globals, i18n } = useContext();

    // @ts-ignore
    const rawAppInfo = ref<AdminAboutInfo>({
      version: "null",
      versionLatest: "null",
    });

    function getAppInfo() {
      const statistics = useAsync(async () => {
        const { data } = await adminApi.about.about();

        if (data) {
          rawAppInfo.value = data;

          const prettyInfo = [
            {
              name: i18n.t("about.version"),
              icon: $globals.icons.information,
              value: data.version,
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
      simpleChecks,
      getColor,
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
</style>