<template>
  <div>
    <v-card class="mt-3">
      <v-card-title class="headline">
        About Mealie
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
          button-text="Download Recipe JSON"
          download-url="/api/debug/last-recipe-json"
        />
        <TheDownloadBtn
          button-text="Download Log"
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
          name: "Version",
          icon: "mdi-information",
          value: debugInfo.version,
        },
        {
          name: "Application Mode",
          icon: "mdi-dev-to",
          value: debugInfo.production ? "Production" : "Development",
        },
        {
          name: "Demo Status",
          icon: "mdi-test-tube",
          value: debugInfo.demoStatus ? "Demo" : "Not Demo",
        },
        {
          name: "API Port",
          icon: "mdi-api",
          value: debugInfo.apiPort,
        },
        {
          name: "API Docs",
          icon: "mdi-file-document",
          value: debugInfo.apiDocs ? "Enabled" : "Disabled",
        },
        {
          name: "Database Type",
          icon: "mdi-database",
          value: debugInfo.dbType,
        },
        {
          name: "SQLite File",
          icon: "mdi-file-cabinet",
          value: debugInfo.sqliteFile,
        },
        {
          name: "Default Group",
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