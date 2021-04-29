<template>
  <div>
    <v-card class="mt-3">
      <v-card-title class="headline">
        {{$t('about.about-mealie')}}
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-list-item-group color="primary">
          <v-list-item v-for="property in prettyInfo" :key="property.name">
            <v-list-item-icon>
              <v-icon> {{ property.icon || "mdi-account" }} </v-icon>
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
      <v-card-actions>
        <v-spacer></v-spacer>
        <TheDownloadBtn
          :button-text="$t('about.download-recipe-json')"
          download-url="/api/debug/last-recipe-json"
        />
        <TheDownloadBtn
          :button-text="$t('about.download-log')"
          download-url="/api/debug/log"
        />
      </v-card-actions>
      <v-divider></v-divider>
    </v-card>
  </div>
</template>

<script>
import { api } from "@/api";
import TheDownloadBtn from "@/components/UI/Buttons/TheDownloadBtn";
export default {
  components: { TheDownloadBtn },
  data() {
    return {
      prettyInfo: [],
    };
  },
  async mounted() {
    await this.getInfo();
  },
  methods: {
    async getInfo() {
      const debugInfo = await api.meta.getDebugInfo();

      this.prettyInfo = [
        {
          name: this.$t('about.version'),
          icon: "mdi-information",
          value: debugInfo.version,
        },
        {
          name: this.$t('about.application-mode'),
          icon: "mdi-dev-to",
          value: debugInfo.production ? this.$t('about.production') : this.$t('about.development'),
        },
        {
          name: this.$t('about.demo-status'),
          icon: "mdi-test-tube",
          value: debugInfo.demoStatus ? this.$t('about.demo') : this.$t('about.not-demo'),
        },
        {
          name: this.$t('about.api-port'),
          icon: "mdi-api",
          value: debugInfo.apiPort,
        },
        {
          name: this.$t('about.api-docs'),
          icon: "mdi-file-document",
          value: debugInfo.apiDocs ? this.$t('general.enabled') : this.$t('general.disabled'),
        },
        {
          name: this.$t('about.database-type'),
          icon: "mdi-database",
          value: debugInfo.dbType,
        },
        {
          name: this.$t('about.sqlite-file'),
          icon: "mdi-file-cabinet",
          value: debugInfo.sqliteFile,
        },
        {
          name: this.$t('about.default-group'),
          icon: "mdi-account-group",
          value: debugInfo.defaultGroup,
        },
      ];
    },
  },
};
</script>

<style lang="scss" scoped>
</style>