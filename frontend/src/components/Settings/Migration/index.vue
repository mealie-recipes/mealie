<template>
  <div>
    <SuccessFailureAlert
      :title="$t('migration.migration-report')"
      ref="report"
      :failedHeader="$t('migration.failed-imports')"
      :failed="failed"
      :successHeader="$t('migration.successful-imports')"
      :success="success"
    />
    <v-card :loading="loading">
      <v-card-title class="headline">
        {{ $t("migration.recipe-migration") }}
      </v-card-title>
      <v-divider></v-divider>
    </v-card>

    <v-row dense>
      <v-col
        :sm="6"
        :md="6"
        :lg="4"
        :xl="3"
        v-for="migration in migrations"
        :key="migration.title"
      >
        <MigrationCard
          :title="migration.title"
          :folder="migration.urlVariable"
          :description="migration.description"
          :available="migration.availableImports"
          @refresh="getAvailableMigrations"
          @imported="showReport"
        />
      </v-col>
    </v-row>
  </div>
</template>


<script>
import MigrationCard from "./MigrationCard";
import SuccessFailureAlert from "../../UI/SuccessFailureAlert";
import api from "../../../api";
export default {
  components: {
    MigrationCard,
    SuccessFailureAlert,
  },
  data() {
    return {
      loading: false,
      success: [],
      failed: [],
      migrations: {
        nextcloud: {
          title: this.$t("migration.nextcloud.title"),
          description: this.$t("migration.nextcloud.description"),
          urlVariable: "nextcloud",
          availableImports: [],
        },
        chowdown: {
          title: this.$t("migration.chowdown.title"),
          description: this.$t("migration.chowdown.description"),
          urlVariable: "chowdown",
          availableImports: [],
        },
      },
    };
  },
  mounted() {
    this.getAvailableMigrations();
  },
  methods: {
    finished() {
      this.loading = false;
      this.$store.dispatch("requestRecentRecipes");
    },
    async getAvailableMigrations() {
      let response = await api.migrations.getMigrations();
      response.forEach(element => {
        if (element.type === "nextcloud") {
          this.migrations.nextcloud.availableImports = element.files;
        } else if (element.type === "chowdown") {
          this.migrations.chowdown.availableImports = element.files;
        }
      });
    },
    showReport(successful, failed) {
      this.success = successful;
      this.failed = failed;
      this.$refs.report.open();
    },
  },
};
</script>

<style>
</style>