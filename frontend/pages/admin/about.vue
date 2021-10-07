<template>
  <v-container fluid>
    <v-card class="mt-3">
      <v-card-title class="headline">
        {{ $t("about.about-mealie") }}
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-list-item-group color="primary">
          <v-list-item v-for="property in appInfo" :key="property.name">
            <v-list-item-icon>
              <v-icon> {{ property.icon || $globals.icons.user }} </v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="pl-4 flex row justify-space-between">
                <div>{{ property.name }}</div>
                <div>{{ property.value }}</div>
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useAsync, useContext } from "@nuxtjs/composition-api";
import { useAdminApi } from "~/composables/use-api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  layout: "admin",
  setup() {
    const adminApi = useAdminApi();
    // @ts-ignore
    const { $globals, i18n } = useContext();

    function getAppInfo() {
      const statistics = useAsync(async () => {
        const { data } = await adminApi.about.about();

        if (data) {
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
      appInfo,
    };
  },
  head() {
    return {
      title: this.$t("about.about") as string,
    };
  },
});
</script>

<style scoped>
</style>